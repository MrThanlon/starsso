# coding: utf-8
import random
import ldap
import ldap.filter
import time
import jwt
import config

from flask import Blueprint, request, session, g, jsonify, current_app
from flask.views import MethodView
from wtforms import Form, StringField, validators

from starsso.utils import check_param, check_login, UNKNOWN_ERROR, send_sms, SMS_FAILED, DUPLICATED_USERNAME, \
    send_email, validate_str, EMAIL_FAILED
from starsso.common.response import make_api_response, OK, INVALID_REQUEST, INVALID_USER, ALREADY_LOGINED

bp = Blueprint('auth_api', __name__)


@bp.route("/login", methods=('POST', 'GET'))
@check_param
def login():
    """
        sso web login API.
    """
    username, password = request.body['username'], request.body['password']
    # validate
    if not validate_str([username, password]):
        return INVALID_REQUEST

    if 'login' in session:
        current_app.logger.info(
            'deny login request with user "{}" for existing session of user "{}"'.format(username, session['username']))
        return ALREADY_LOGINED

    # search user to bind.
    l = current_app.get_ldap_connection()
    user_entries = l.search_s(current_app.ldap_search_base,
                              ldap.SCOPE_SUBTREE,
                              current_app.ldap_search_pattern.format(
                                  username=ldap.filter.escape_filter_chars(username)))
    if not user_entries:  # user not found
        current_app.logger.info('deny login request with username "{}". username not found.'.format(username))
        return INVALID_USER
    if len(user_entries) > 1:  # ambiguous username. not allow to login.
        current_app.logger.warn('ambiguous username "{}". login request is deined.'.format(username))
        return INVALID_USER
    user_entry = user_entries[0]

    # re-bind according to user dn.
    user_dn = user_entry[0]
    attrs = user_entry[1]
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
    if b'admin' in attrs.get(current_app.ldap_attr_permission):
        session['admin'] = True
    else:
        session['admin'] = False
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
                              current_app.ldap_search_pattern.format(
                                  username=ldap.filter.escape_filter_chars(username)))
    if not user_entries:  # impossible?
        current_app.logger.warn('username {} not found, fatal error.'.format(username))
        return UNKNOWN_ERROR
    if len(user_entries) > 1:  # ambiguous username. not allow to login.
        current_app.logger.warn('ambiguous username "{}". login request is deined.'.format(username))
        return INVALID_USER, 'Duplicated users found. The users are blocked for security reason. Consult administrator to get help.'
    user_entry = user_entries[0]
    attrs = user_entry[1]
    if request.body.get('email'):
        # query email
        if not send_email(attrs[current_app.ldap_attr_email][0].decode('utf-8'), code, username):
            current_app.logger.error(
                'Failed to send email, {}, check configuration.'.format(
                    attrs[current_app.ldap_attr_email][0].decode('utf-8')))
            return EMAIL_FAILED
    elif request.body.get('phone'):
        if not send_sms(attrs[current_app.ldap_attr_phone][0].decode('utf-8'), code):
            current_app.logger.error(
                'Failed to send SMS, phone: {}, check configuration.'.format(
                    attrs[current_app.ldap_attr_phone][0].decode('utf-8')))
            return SMS_FAILED

    # set session
    session['validation_code'] = code
    session['validation_expire'] = time.time() + current_app.validation_expiration
    return 0


@bp.route("/register", methods=('POST', 'GET'))
@check_param
def register():
    # verify invite code
    code = request.body['inviteCode']
    username = request.body['username']
    password = request.body['password']
    full_name = request.body[current_app.ldap_attr_name]
    email = request.body['email']
    # validate
    if not validate_str([code, username, password, full_name, email]):
        return INVALID_REQUEST
    # code is jwt, decode it
    try:
        decode = jwt.decode(code, config.SECRET_KEY)
    except jwt.DecodeError:
        return -100
    # code include email and birthday
    if decode['email'] != email:
        return -11
    token = current_app.db.query(current_app.Validaton).filter_by(code=decode['code'])
    if not token:
        return -11
    if time.time() > decode['expire']:
        return -11
    # check username
    # FIXME: Reused
    l = current_app.get_ldap_connection()
    user_entries = l.search_s(current_app.ldap_search_base,
                              ldap.SCOPE_SUBTREE,
                              current_app.ldap_search_pattern.format(
                                  username=ldap.filter.escape_filter_chars(username)))
    if user_entries:  # username has been taken
        return DUPLICATED_USERNAME
    user_dn = 'cn={},'.format(ldap.dn.escape_dn_chars(username)) + config.LDAP_SEARCH_BASE
    # register
    l.add_s(user_dn, [('objectClass', [b'organizationalPerson', b'person', b'starstudioMember', b'top']),
                      (current_app.ldap_attr_email, email.encode('utf-8')),
                      (current_app.ldap_attr_name, full_name.encode('utf-8'))])
    l.passwd_s(user_dn, None, password.encode('ascii'))
    # remove code
    current_app.db.session.delete(token)
    current_app.db.session.commit()
    # set session
    # FIXME: Reused
    session['username'] = username
    session['login'] = True
    session['born'] = time.time()
    current_app.logger.info('user "{}" registered. (ldap dn: {})'.format(username, user_dn))
    return 0
