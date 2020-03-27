# coding: utf-8

from flask import Blueprint, request, session, current_app

import ldap

from starsso.utils import check_param, check_login, UNKNOWN_ERROR, send_sms, SMS_FAILED, DUPLICATED_USERNAME, \
    INVALID_USER, OK

import config

bp = Blueprint('profile_api', __name__)


@bp.route("/profile/modify", methods=('GET', 'POST'))
@check_param
@check_login
def profile_modify():
    username = session['username']
    password = request.body['password']
    new_password = request.body.get('newPassword')
    email = request.body.get('email')
    phone = request.body.get('phone')
    vefify = request.body['verify']
    if vefify != session['code']:
        return -30

    # FIXME: reused
    l = current_app.get_ldap_connection()
    user_entries = l.search_s(current_app.ldap_search_base,
                              ldap.SCOPE_SUBTREE,
                              current_app.ldap_search_pattern.format(username=username))
    if not user_entries:  # impossible?
        current_app.logger.info('deny modify request with username "{}". username not found.'.format(username))
        return INVALID_USER
    if len(user_entries) > 1:  # ambiguous username. not allow to login.
        current_app.logger.warn('ambiguous username "{}". login request is deined.'.format(username))
        return INVALID_USER, 'Duplicated users found. The users are blocked for security reason. Consult administrator to get help.'
    user_entry = user_entries[0]

    # re-bind according to user dn.
    user_dn = user_entry[0]
    try:
        l.simple_bind_s(user_dn, password)
    except ldap.INVALID_CREDENTIALS:
        current_app.logger.info('login with username {}. invalid password.'.format(username))
        return INVALID_USER

    # TODO: generate modlist, modify entries, catch exception
    modlist = []
    if email:
        modlist.append(('email', email.encode('utf-8')))
    if phone:
        modlist.append(('telephoneNumber', phone.encode('utf-8')))
    l.modify_s(user_dn, modlist)
    if new_password:
        l.passwd_s(user_dn, None, new_password.encode('utf-8'))

    return OK


@bp.route("/profile", methods=('GET', 'POST'))
@check_param
@check_login
def profile():
    username = session['username']
    l = current_app.get_ldap_connection()
    user_entries = l.search_s(current_app.ldap_search_base,
                              ldap.SCOPE_SUBTREE,
                              current_app.ldap_search_pattern.format(username=username))
    if not user_entries:  # impossible?
        current_app.logger.warn('username {} not found, fatal error.'.format(username))
        return UNKNOWN_ERROR
    user_entry = user_entries[0]
    attrs = user_entry[1]
    return {"username": username, "email": attrs['telephoneNumber'], "phone": "none"}
