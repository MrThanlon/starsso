# coding: utf-8

from flask import Blueprint

bp = Blueprint('auth_api', __name__)

@bp.route("/login", methods=('POST',))
def login():
    pass

@bp.route("/validation_code", methods=('POST',))
def validation_code():
    pass

@bp.route("/register", methods=('POST',))
def register():
    pass