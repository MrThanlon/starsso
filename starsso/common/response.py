# coding: utf-8

"""
Error message
"""

OK = 0
INVALID_REQUEST = -1
INVALID_USER = -37
ALREADY_LOGINED = -2


ERROR_MESSAGES = {
    OK: 'ok',
    INVALID_REQUEST: 'bad request params',
    INVALID_USER: 'wrong name or password',
    ALREADY_LOGINED: 'logged',
    
    -11: 'wrong invite code',
    -23: 'repeated name',
    -30: 'wrong validation code',
    -33: 'expired cookie',
    -100: 'unknown error'
}


def make_api_response(data=None, code=None, msg=None):
    '''
        make_response() makes response fitted with convention.
    '''
    
    if code is None:
        code = 0
    if msg is None:
        msg = ERROR_MESSAGES.get(code, 'unknown error')
        
    return {"code": code, "msg": msg, "data": data}