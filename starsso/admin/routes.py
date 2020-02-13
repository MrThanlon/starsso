# coding: utf-8

from flask import Blueprint

from .auth import bp as auth_bp

def register(app, url_prefix):
    app.register_blueprint(auth_bp, url_prefix=url_prefix) # auth bp