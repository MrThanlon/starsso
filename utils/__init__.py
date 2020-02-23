# coding: utf-8
"""
关于session：
    session中保存的信息有
    - login: 是否登录
    - born: 生日
    - code: 验证码（如果有）
"""
from flask import jsonify, Response, Request, session

"""
Error message
"""
errorMessage = {
    0: 'ok',
    -2: 'logged',
    -1: 'bad request params',
    -11: 'wrong invite code',
    -23: 'repeated name',
    -30: 'wrong validation code',
    -33: 'expired cookie',
    -37: 'wrong name or password',
    -100: 'unknown error'
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
        if isinstance(response, (list, dict)):
            # return with data
            body['data'] = response
        elif isinstance(response, int):
            # return with error code
            body['code'] = response
        else:
            # error type
            body['code'] = -100

        try:
            body['msg'] = errorMessage[body['code']]
        except KeyError:
            body['code'] = -100
        finally:
            body['msg'] = errorMessage[body['code']]
        response = jsonify(body)
        return super(Response, cls).force_type(response, environ)


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


class JWT:
    def __init__(self, username):
        self.username = username


def check_param(f):
    """
    Return -1 if missing param.
    FIXME: with param list
    :param f: function
    :return: wrapped
    """

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

    def wrapped():
        if 'login' not in session:
            return -33
        return f()

    return wrapped
