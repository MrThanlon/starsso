# coding: utf-8
import random
import ldap
import time
import jwt
import config

from flask import Blueprint, request, session, g, jsonify, current_app
from flask.views import MethodView
from wtforms import Form, StringField, validators

from starsso.utils import check_param, check_login, UNKNOWN_ERROR, send_sms, SMS_FAILED, DUPLICATED_USERNAME, send_email
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


@bp.route("/logout", methods=('POST', 'GET'))
@check_param
@check_login
def logout():
    # TODO: remove from database
    session.clear()
    return OK


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
        if not send_email(attrs['email'], code):
            current_app.logger.warn(
                'Failed to send email, {}, check configuration.'.format(attrs['email']))
            return SMS_FAILED
    elif request.body['phone']:
        if not send_sms(attrs['telephoneNumber'], code):
            current_app.logger.warn(
                'Failed to send SMS, phone: {}, check configuration.'.format(attrs['telephoneNumber']))
            return SMS_FAILED

    # set session
    session['code'] = code
    return 0


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
    # TODO: add an entry, with telephone number
    l.add_s(user_dn, [('objectClass', [b'organizationalPerson', b'person', b'starstudioMember', b'top']),
                      ('email', bytes(email.encode('utf-8')))])
    # set session
    # FIXME: Reused
    session['username'] = username
    session['login'] = True
    session['born'] = time.time()
    current_app.logger.info('user "{}" registered. (ldap dn: {})'.format(username, user_dn))
    return 0
