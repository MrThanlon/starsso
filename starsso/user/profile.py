# coding: utf-8

from flask import Blueprint, request, session, current_app, jsonify
import ldap
import ldap.filter
import time
from starsso.utils import check_param, check_login, UNKNOWN_ERROR, send_sms, SMS_FAILED, DUPLICATED_USERNAME, \
    INVALID_USER, OK, validate_str, INVALID_REQUEST, EXISTENT_EMAIL

import config

bp = Blueprint('profile_api', __name__)


@bp.route("/profile/modify", methods=('GET', 'POST'))
@check_param
@check_login
def profile_modify():
    username = session['username']
    password = request.body.get('password')
    new_password = request.body.get('newPassword')
    phone = request.body.get('phone')
    full_name = request.body.get('fullName')
    verify = request.body.get('verify')

    # FIXME: reused
    l = current_app.get_ldap_connection()
    user_entries = l.search_s(current_app.ldap_search_base,
                              ldap.SCOPE_SUBTREE,
                              current_app.ldap_search_pattern.format(
                                  username=ldap.filter.escape_filter_chars(username)))
    if not user_entries:  # impossible?
        current_app.logger.info('deny modify request with username "{}". username not found.'.format(username))
        return INVALID_USER
    if len(user_entries) > 1:  # ambiguous username. not allow to login.
        current_app.logger.warn('ambiguous username "{}". login request is deined.'.format(username))
        return INVALID_USER, 'Duplicated users found. The users are blocked for security reason. Consult administrator to get help.'
    user_entry = user_entries[0]
    user_dn = user_entry[0]

    # sensitive information
    if new_password or phone:
        if isinstance(verify, str):
            # trans to int
            try:
                verify = int(verify)
            except ValueError:
                return INVALID_REQUEST
        if not isinstance(verify, int):
            return INVALID_REQUEST
        if verify != session['validation_code'] or session['validation_expire'] > time.time():
            return -30
        # re-bind according to user dn.
        if not validate_str([password]):
            return INVALID_REQUEST
        try:
            l.simple_bind_s(user_dn, password)
        except ldap.INVALID_CREDENTIALS:
            current_app.logger.info('login with username {}. invalid password.'.format(username))
            return INVALID_USER

    l = current_app.get_ldap_connection()
    # TODO: generate modlist, modify entries
    # FIXME: catch exception
    modlist = []
    if phone:
        if not validate_str([phone]):
            return INVALID_REQUEST
        modlist.append((ldap.MOD_REPLACE, current_app.ldap_attr_phone, ldap.filter.escape_filter_chars(phone).encode('utf-8')))
    if full_name:
        if not validate_str([full_name]):
            return INVALID_REQUEST
        modlist.append((ldap.MOD_REPLACE, current_app.ldap_attr_name, ldap.filter.escape_filter_chars(full_name).encode('utf-8')))
    if modlist:
        l.modify_s(user_dn, modlist)
    if new_password:
        if not validate_str([new_password]):
            return INVALID_REQUEST
        l.passwd_s(user_dn, None, new_password.encode('ascii'))

    return OK


@bp.route("/profile", methods=('GET', 'POST'))
@check_param
@check_login
def profile():
    username = session['username']
    l = current_app.get_ldap_connection()
    user_entries = l.search_s(current_app.ldap_search_base,
                              ldap.SCOPE_SUBTREE,
                              current_app.ldap_search_pattern.format(
                                  username=ldap.filter.escape_filter_chars(username)))
    if not user_entries:  # impossible?
        current_app.logger.warn('username {} not found, fatal error.'.format(username))
        return UNKNOWN_ERROR
    user_entry = user_entries[0]
    attrs = user_entry[1]
    return {
        "username": username,
        "email": attrs[current_app.ldap_attr_email][0].decode('utf-8'),
        "phone": attrs.get(current_app.ldap_attr_phone)[0].decode('utf-8'),
        "fullName": attrs.get(current_app.ldap_attr_name)[0].decode('utf-8'),
        "admin": b'admin' in attrs.get(current_app.ldap_attr_permission)
    }
