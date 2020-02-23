# coding: utf-8

from flask import Blueprint, request, session

import utils
import config

bp = Blueprint('profile_api', __name__)


@bp.route("/profile/modify", methods=('GET', 'POST'))
@utils.check_param
@utils.check_login
def profile_modify():
    # check validation
    if session['code'] != request.body['verify']:
        return -30
    # check password
    pass
    # modify!
    if 'username' in request.body:
        pass
    if 'newPassword' in request.body:
        pass
    if 'email' in request.body:
        pass
    if 'phone' in request.body:
        pass
    return 0


@bp.route("/profile", methods=('GET', 'POST'))
@utils.check_param
@utils.check_login
def profile():
    return {
        'username': session['username'],
        'email': '',
        'phone': ''
    }
