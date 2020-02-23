# coding: utf-8

from flask import Blueprint

import utils

bp = Blueprint('user_permission_api', __name__)


@bp.route("/", methods=('GET', 'POST'))
@utils.check_login
def profile_modify():
    return []
