# coding: utf-8

from flask import Blueprint

bp = Blueprint('user_permission_api', __name__)

@bp.route("/", methods=('GET',))
def profile_modify():
    pass
