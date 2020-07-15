# coding: utf-8
"""
关于session：
    session中保存的信息有
    - login: 是否登录
    - born: session生成时间
    - username: 登录名
    - code: 验证码（如果有）
"""
import config
import smtplib
import ldap
import ldap.filter
from email.mime.text import MIMEText
from email.header import Header
from flask import jsonify, Response, Request, session, current_app, Flask
from flask.json import JSONEncoder
from flask_sqlalchemy import SQLAlchemy

import functools

"""
Error message
"""
OK = 0
INVALID_REQUEST = -1
INVALID_USER = -37
ALREADY_LOGINED = -2
SMS_FAILED = -40
EMAIL_FAILED = -41
DUPLICATED_USERNAME = -42
DUPLICATED_NAME = -43
NOT_ADMIN = -51
NOT_EXISTENT_ID = -53
INCLUDE_NON_EXISTENT_USERNAME = -55
EXISTENT_EMAIL = -57
NOT_EXISTENT_NAME = -59
UNKNOWN_ERROR = -100

ERROR_MESSAGES = {
    OK: 'ok',
    INVALID_REQUEST: 'bad request params',
    INVALID_USER: 'wrong name or password',
    ALREADY_LOGINED: 'logged',

    -11: 'wrong invite code',
    -23: 'repeated name',
    -30: 'wrong validation code',
    -33: 'expired cookie',
    SMS_FAILED: 'failed to send sms',
    EMAIL_FAILED: 'failed to send email',
    DUPLICATED_USERNAME: 'duplicated username',
    DUPLICATED_NAME: 'duplicated name',
    NOT_ADMIN: 'not admin',
    NOT_EXISTENT_ID: 'non-existent ID',
    INCLUDE_NON_EXISTENT_USERNAME: 'users list includes non-existent username',
    EXISTENT_EMAIL: 'existent email address',
    NOT_EXISTENT_NAME: 'non-existent name',
    UNKNOWN_ERROR: 'unknown error'
}


class MiniJSONEncoder(JSONEncoder):
    """Minify JSON output."""
    item_separator = ','
    key_separator = ':'


class APIResponse(Response):
    @classmethod
    def force_type(cls, response, environ=None):
        """
        Simplify handle function.
        :param response: a response object or wsgi application.
        :param environ: a WSGI environment object.
        :return: a response object.
        """
        body = {'code': 0}
        if isinstance(response, tuple):
            # return ERROR_CODE with custom message
            body['code'], body['msg'] = response
        elif isinstance(response, (list, dict)):
            # return with data
            body['data'] = response
        elif isinstance(response, int):
            # return with error code
            body['code'] = response
        else:
            # error type
            body['code'] = -100

        if 'msg' not in body:
            try:
                body['msg'] = ERROR_MESSAGES[body['code']]
            except KeyError:
                # TODO: logger, unknown code
                body['code'] = -100
            finally:
                body['msg'] = ERROR_MESSAGES[body['code']]
        return super(Response, cls).force_type(jsonify(body), environ)


class APIRequest(Request):
    def __init__(self, environ, populate_request=True, shallow=False):
        self.body = {}
        Request.__init__(self, environ, populate_request=True, shallow=False)

    def parse(self):
        """
        Call before request.
        :return: Boolean
        """
        if self.method == 'GET':
            self.body = self.args
            return True
        elif self.method == 'POST':
            if self.content_type == 'application/json':
                self.body = self.get_json()
            elif self.content_type == 'application/x-www-form-urlencoded':
                self.body = self.form.to_dict()
            elif self.content_type is None:
                self.body = {}
            elif self.content_type.startswith('multipart/form-data'):
                # FIXME: file content
                self.body = self.form.to_dict()
                if self.files:
                    return False
            else:
                return False
            return True
        else:
            return False


class StarFlask(Flask):
    def make_response(self, rv):
        if isinstance(rv, int):
            msg = ERROR_MESSAGES.get(rv)
            if not msg:
                msg = ERROR_MESSAGES[UNKNOWN_ERROR]
            return super().make_response({'code': rv, 'msg': msg})
        elif isinstance(rv, list) or isinstance(rv, dict):
            return super().make_response({'code': OK, 'msg': ERROR_MESSAGES.get(OK), 'data': rv})
        else:
            return super().make_response(rv)


def check_param(f):
    """
    Return -1 if missing param.
    FIXME: with param list
    :param f: function
    :return: wrapped
    """

    @functools.wraps(f)
    def wrapped():
        try:
            return f()
        except KeyError as e:
            current_app.logger.warn(e)
            return -1

    return wrapped


def check_login(f):
    """
    Return -33 if not logged.
    :param f:
    :return:
    """

    @functools.wraps(f)
    def wrapped():
        if 'login' not in session:
            return -33
        return f()

    return wrapped


def check_username(f):
    """
    Check if user is invalid
    :param f:
    :return:
    """

    @functools.wraps(f)
    def wrapped():
        username = session['username']
        l = current_app.get_ldap_connection()
        user_entries = l.search_s(current_app.ldap_search_base,
                                  ldap.SCOPE_SUBTREE,
                                  current_app.ldap_search_pattern.format(
                                      username=ldap.filter.escape_filter_chars(username)))
        if not user_entries:  # impossible?
            current_app.logger.warn('username {} not found, fatal error.'.format(username))
            return -33
        if len(user_entries) > 1:  # ambiguous username. not allow to login.
            current_app.logger.warn('ambiguous username "{}". login request is deined.'.format(username))
            return INVALID_USER, 'Duplicated users found. The users are blocked for security reason. Consult administrator to get help.'
        return f()

    return wrapped


def check_admin(f):
    """
    Return -51 if not admin.
    :param f:
    :return:
    """

    @functools.wraps(f)
    def wrapped():
        username = session['username']
        if not session.get('admin'):
            current_app.logger.warn('None-admin user request admin API, denied.'.format(username))
            return NOT_ADMIN
        # real-time check for security reason
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
        if b'admin' not in attrs.get(current_app.ldap_attr_permission):
            current_app.logger.warn('None-admin user request admin API, denied.'.format(username))
            return NOT_ADMIN
        return f()

    return wrapped


# FIXME: separate invite and validation
def send_sms(phone, code):
    # TODO: SMS
    return False


def send_email(email, code, user):
    receivers = [email]
    message = MIMEText('Your validation code is {}, use it in 5m.'.format(code), 'plain', 'utf-8')
    message['From'] = Header('StarSSO', 'utf-8')
    message['To'] = Header(user, 'utf-8')
    message['Subject'] = Header('StarSSO Validation Code', 'utf-8')
    try:
        smtp = smtplib.SMTP_SSL(config.SMTP_HOST, 465)
        smtp.connect(config.SMTP_HOST, 465)
        smtp.login(config.SMTP_USER, config.SMTP_PASS)
        smtp.sendmail(config.SMTP_SENDER, email, message.as_string())
    except smtplib.SMTPException as e:
        current_app.logger.warn(e)
        return False
    return True


def validate_str(l):
    for i in l:
        if (not isinstance(i, str)) or (len(i) == 0):
            return False

    return True
