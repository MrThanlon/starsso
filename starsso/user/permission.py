# coding: utf-8

from flask import Blueprint

from starsso.utils import check_login

bp = Blueprint('user_permission_api', __name__)

@bp.route("/", methods=('GET', 'POST'))
@check_login
def profile_modify():
    return []
