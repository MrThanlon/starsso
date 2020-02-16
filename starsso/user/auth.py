# coding: utf-8

from flask import Blueprint, request, session, g

bp = Blueprint('auth_api', __name__)


@bp.route("/login", methods=('POST', 'GET'))
def login():
    return request.body


@bp.route("/validationCode", methods=('POST', 'GET'))
def validation_code():
    return {'hello': 'world'}


@bp.route("/register", methods=('POST', 'GET'))
def register():
    return -1
