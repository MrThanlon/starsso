# coding: utf-8

from flask import Blueprint

from .system import bp as system_bp
from .user import bp as user_bp
from .application import bp as application_bp


def register(app, url_prefix):
    app.register_blueprint(system_bp, url_prefix=url_prefix + '/system')  # auth bp
    app.register_blueprint(user_bp, url_prefix=url_prefix + '/user')
    app.register_blueprint(application_bp, url_prefix=url_prefix)
