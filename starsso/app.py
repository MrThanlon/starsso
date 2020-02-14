# coding: utf-8

from flask import Flask, jsonify

from utils import APIResponse

from .admin import routes as admin_routes
from .user import routes as user_routes


def get_wsgi_application():
    app = Flask(__name__)

    user_routes.register(app, url_prefix="/user")
    admin_routes.register(app, url_prefix="/admin")
    app.response_class = APIResponse

    return app


app = get_wsgi_application()
