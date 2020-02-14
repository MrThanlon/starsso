# coding: utf-8

from flask import Blueprint

bp = Blueprint('auth_api', __name__)


@bp.route("/login", methods=('POST', 'GET'))
def login():
    return 0


@bp.route("/validationCode", methods=('POST', 'GET'))
def validation_code():
    return {'hello': 'world'}


@bp.route("/register", methods=('POST', 'GET'))
def register():
    return 0
