from flask import Flask, jsonify
import os
import importlib


def create_app():
    app = Flask(__name__)
    # scan controller
    dirs = os.listdir('./controllers')
    for c in dirs:
        bp = importlib.import_module('controllers.' + c)
        app.register_blueprint(bp.bp)

    return app
