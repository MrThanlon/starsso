# coding: utf-8
import random
import ldap

from flask import Blueprint, request, session, g, jsonify, current_app
from flask.views import MethodView
from wtforms import Form, StringField, validators

from starsso.utils import check_param, check_login
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
            'deny login request with user "{}" for existing session of user "{}"'.format(username, self.current_user))
        return ALREADY_LOGINED

    # search user to bind.
    l = current_app.get_ldap_connection()
    user_entries = l.search_s(current_app.ldap_search_base,
                              ldap.SCOPE_SUBTREE,
                              current_app.ldap_search_pattern.format(username=username))
    if not user_entries:  # user not found
        current_app.logger.info('deny login request with username "{}". username not found.'.format(username))
        return INVALID_USER
    if len(user_entries) > 1:  # ambigous username. not allow to login.
        current_app.logger.warn('ambigous username "{}". login request is deined.'.format(username))
        # FIXME: Duplicated users found. The users are blocked for security reason. Consult administrator to get help.
        return INVALID_USER
    user_entry = user_entries[0]

    # re-bind according to user dn.
    user_dn = user_entry[0]
    try:
        l.simple_bind_s(user_dn, password)
    except ldap.INVALID_CREDENTIALS:
        current_app.logger.info('login with username {}. invalid password.'.format(username))
        return INVALID_USER

    # valid account. register session.
    session['username'] = username
    current_app.logger.info('user "{}" logined. (ldap dn: {})'.format(username, user_dn))

    return OK


@bp.route("/validationCode", methods=('POST', 'GET'))
@check_param
@check_login
def validation_code():
    # generate code
    # FIXME: not secure, switch to random.org
    code = random.randint(100000, 999999)
    # send code via email or sms
    if request.body['email']:
        pass
    elif request.body['phone']:
        pass
    # set session
    session['code'] = code
    return 0


@bp.route("/register", methods=('POST', 'GET'))
@check_param
def register():
    # verify invite code
    pass
    # register!
    pass
    # set session
    return 0
