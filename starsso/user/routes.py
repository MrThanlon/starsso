# coding: utf-8

from flask import Blueprint

from .auth import bp as auth_bp
from .profile import bp as profile_bp
from .permission import bp as permission_bp


def register(app, url_prefix):
    # auth api.
    app.register_blueprint(auth_bp, url_prefix=url_prefix)
    # profile api.
    app.register_blueprint(profile_bp, url_prefix=url_prefix)
    # permission api.
    app.register_blueprint(permission_bp, url_prefix=url_prefix)
