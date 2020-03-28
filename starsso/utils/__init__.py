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
from email.mime.text import MIMEText
from email.header import Header
from flask import jsonify, Response, Request, session

import functools

"""
Error message
"""
OK = 0
INVALID_REQUEST = -1
INVALID_USER = -37
ALREADY_LOGINED = -2
SMS_FAILED = -40
DUPLICATED_USERNAME = -42
NOT_ADMIN = -51
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
    DUPLICATED_USERNAME: 'duplicated username',
    NOT_ADMIN: 'not admin',
    UNKNOWN_ERROR: 'unknown error'
}


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
                self.body = self.form
            elif self.content_type.startswith('multipart/form-data'):
                # FIXME: file content
                self.body = self.form
                if self.files:
                    return False
            else:
                return False
            return True
        else:
            return False


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
        except KeyError:
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


def check_admin(f):
    """
    Return -51 if not admin.
    :param f:
    :return:
    """

    @functools.wraps(f)
    def wrapped():
        if 'admin' not in session:
            return NOT_ADMIN
        return f()

    return wrapped


def send_sms(phone, code, user):
    # TODO: SMS
    return False


def send_email(email, code, user):
    receivers = [email]
    message = MIMEText('{}'.format(code), 'plain', 'utf-8')
    message['From'] = Header("StarSSO", 'utf-8')
    message['To'] = Header(user, 'utf-8')
    message['Subject'] = Header('[StarSSO] Validation Code', 'utf-8')
    try:
        smtp = smtplib.SMTP()
        # FIXME: use SSL, not port 25?
        smtp.connect(config.SMTP_HOST, 25)
        smtp.login(config.SMTP_USER, config.SMTP_PASS)
        smtp.sendmail(config.SMTP_SENDER, receivers, message.as_string())
    except smtplib.SMTPException:
        return False
    return True
