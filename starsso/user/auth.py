# coding: utf-8
import random
import ldap
import time
import jwt
import config

from flask import Blueprint, request, session, g, jsonify, current_app
from flask.views import MethodView
from wtforms import Form, StringField, validators

from starsso.utils import check_param, check_login, UNKNOWN_ERROR, send_sms, SMS_FAILED, DUPLICATED_USERNAME
from starsso.common.response import make_api_response, OK, INVALID_REQUEST, INVALID_USER, ALREADY_LOGINED

bp = Blueprint('auth_api', __name__)


@bp.route("/login", methods=('POST', 'GET'))
@check_param
def login():
    """
        sso web login API.
    """
    username, password = request.body.username, request.body.password

    if session.login:
        current_app.logger.info(
            'deny login request with user "{}" for existing session of user "{}"'.format(username, session['username']))
        return ALREADY_LOGINED

    # search user to bind.
    l = current_app.get_ldap_connection()
    user_entries = l.search_s(current_app.ldap_search_base,
                              ldap.SCOPE_SUBTREE,
                              current_app.ldap_search_pattern.format(username=username))
    if not user_entries:  # user not found
        current_app.logger.info('deny login request with username "{}". username not found.'.format(username))
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

    # valid account. register session.
    # FIXME: Reused
    session['username'] = username
    session['login'] = True
    session['born'] = time.time()
    current_app.logger.info('user "{}" logined. (ldap dn: {})'.format(username, user_dn))

    return OK


@bp.route("/loout", methods=('POST', 'GET'))
@check_param
@check_login
def logout():
    # TODO: remove from database
    session.clear()
    return OK


@bp.route("/profile", methods=('POST', 'GET'))
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


@bp.route("/validationCode", methods=('POST', 'GET'))
@check_param
@check_login
def validation_code():
    """
        generate code.
    """
    # FIXME: not secure, switch to random.org
    code = random.randint(100000, 999999)
    # send code via email or sms
    username = session['username']
    l = current_app.get_ldap_connection()
    user_entries = l.search_s(current_app.ldap_search_base,
                              ldap.SCOPE_SUBTREE,
                              current_app.ldap_search_pattern.format(username=username))
    if not user_entries:  # impossible?
        current_app.logger.warn('username {} not found, fatal error.'.format(username))
        return UNKNOWN_ERROR
    if len(user_entries) > 1:  # ambiguous username. not allow to login.
        current_app.logger.warn('ambiguous username "{}". login request is deined.'.format(username))
        return INVALID_USER, 'Duplicated users found. The users are blocked for security reason. Consult administrator to get help.'

    user_entry = user_entries[0]
    attrs = user_entry[1]
    if request.body['email']:
        # query email
        pass
    elif request.body['phone']:
        if not send_sms(attrs['telephoneNumber']):
            current_app.logger.warn(
                'Failed to send SMS, phone: {}, check configuration.'.format(attrs['telephoneNumber']))
            return SMS_FAILED

    # set session
    session['code'] = code
    return 0


@bp.route("/profile/modify", methods=('POST', 'GET'))
@check_param
@check_login
def profile_modify():
    # TODO: change entry
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
    return OK


@bp.route("/register", methods=('POST', 'GET'))
@check_param
def register():
    # verify invite code
    code = request.body['inviteCode']
    username = request.body['username']
    password = request.body['password']
    email = request.body['email']
    # code is jwt, decode it
    try:
        decode = jwt.decode(code, config.SECRET_KEY, algorithms='HS256')
    except jwt.exceptions.InvalidSignatureError:
        return -30
    except jwt.DecodeError:
        return -100
    # code include email and birthday
    if decode['email'] != email:
        return -30
    # check username
    l = current_app.get_ldap_connection()
    user_entries = l.search_s(current_app.ldap_search_base,
                              ldap.SCOPE_SUBTREE,
                              current_app.ldap_search_pattern.format(username=username))
    if user_entries:  # username has been taken
        return DUPLICATED_USERNAME
    # FIXME: escape string
    user_dn = 'cn={},'.format(username) + config.LDAP_SEARCH_BASE
    # register
    # TODO: add an entry
    pass
    # set session
    # FIXME: Reused
    session['username'] = username
    session['login'] = True
    session['born'] = time.time()
    current_app.logger.info('user "{}" registered. (ldap dn: {})'.format(username, user_dn))
    return 0


@bp.route("/permission", methods=('POST', 'GET'))
@check_param
@check_login
def permission():
    username = session['username']
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
    attrs = user_entry[1]
    # TODO: get the list of permission
    return OK
