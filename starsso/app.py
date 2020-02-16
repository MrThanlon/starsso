# coding: utf-8

from flask import Flask, jsonify, request

import utils
import config

from .admin import routes as admin_routes
from .user import routes as user_routes


def get_wsgi_application():
    app = Flask(__name__)
    app.secret_key = config.session_secret
    app.response_class = utils.APIResponse
    app.request_class = utils.APIRequest

    @app.before_request
    def before_request():
        request.parse()

    user_routes.register(app, url_prefix="/user")
    admin_routes.register(app, url_prefix="/admin")

    return app


app = get_wsgi_application()
