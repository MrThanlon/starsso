# coding: utf-8
from flask import jsonify, Response

errorMessage = {
    0: 'ok',
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
