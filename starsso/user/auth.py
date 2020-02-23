# coding: utf-8
import time
import random
from flask import Blueprint, request, session, g

import utils
import config

bp = Blueprint('auth_api', __name__)


@bp.route("/login", methods=('POST', 'GET'))
@utils.check_param
def login():
    # verify username
    username = request.body['username']
    password = request.body['password']
    # set session
    session['login'] = True
    session['username'] = request.body['username']
    session['born'] = time.time()
    return 0


@bp.route("/validationCode", methods=('POST', 'GET'))
@utils.check_param
@utils.check_login
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
@utils.check_param
def register():
    # verify invite code
    pass
    # register!
    pass
    # set session
    return 0
