# coding: utf-8

from flask import Blueprint

bp = Blueprint('profile_api', __name__)

@bp.route("/profile/modify", methods=('POST',))
def profile_modify():
    pass

@bp.route("/profile", methods=('GET',))
def profile():
    pass