# coding: utf-8

from flask import Flask, jsonify, request, abort, g, session, send_from_directory, send_file
from flask_sqlalchemy import SQLAlchemy

from datetime import timedelta

from starsso.utils import APIResponse, APIRequest, StarFlask, MiniJSONEncoder

import ldap
import weakref
import os
import logging

import config

from starsso.admin import routes as admin_routes
from starsso.user import routes as user_routes


def register_services(app):
    '''
        register_services() inserts common service methods.
    '''

    # LDAP
    def get_ldap_connection():
        '''
            establish new ldap connection.
        '''
        l = ldap.initialize(app.ldap_uri)
        l.simple_bind_s(app.ldap_root_bind_dn, app.ldap_password)
        weakref.finalize(l, l.unbind_s)  # prevent connection leaks.
        return l

    app.get_ldap_connection = get_ldap_connection

    # Log
    log_driver_type = app.config.get('LOG_STORAGE_DRIVER', 'file')
    if log_driver_type == 'file':
        log_file_name = app.config.get('LOG_STORAGE_FILE_NAME', 'starsso.log')
        file_handler = logging.FileHandler(filename=log_file_name)
        file_handler.setFormatter(
            logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s")
        )
        app.logger.addHandler(file_handler)
        if app.debug:
            file_handler.setLevel(logging.DEBUG)
        else:
            file_handler.setLevel(logging.INFO)


def register_db(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://{username}:{password}@{host}:{port}/{name}".format(
        username=app.db_user,
        password=app.db_pass,
        host=app.db_host,
        port=app.db_port,
        name=app.db_name
    )
    db = SQLAlchemy(app)
    db.reflect()

    class System(db.Model):
        __tablename__ = 'system'

        def __init__(self, name, url='', public=True):
            self.name = name
            self.url = url
            self.public = public

        def add(self):
            db.session.add(self)
            return db.session.commit()

    class Invite(db.Model):
        __tablename__ = 'invite'

        def __init__(self, code):
            self.code = code

        def add(self):
            db.session.add(self)
            return db.session.commit()

    class Application(db.Model):
        __tablename__ = 'application'

        def __init__(self, username, name):
            self.username = username
            self.name = name

        def add(self):
            db.session.add(self)
            return db.session.commit()

    app.db = db
    app.System = System
    app.Invite = Invite
    app.Application = Application


def register_routes(app):
    user_routes.register(app, url_prefix="/user")
    admin_routes.register(app, url_prefix="/admin")


def load_configuration(app):
    config_file = os.path.abspath(os.environ.get('STARSSO_CONFIG_FILE', 'config.py'))
    app.config.from_pyfile(filename=config_file)

    app.validation_expiration = app.config.get('VALIDATION_EXPIRATION', 300)

    # DB
    app.db_host = app.config.get('DATABASE_HOST')
    if not app.db_host:
        raise "DATABASE_HOST missing."
    app.db_user = app.config.get('DATABASE_USER')
    if not app.db_user:
        raise "DATABASE_USER missing."
    app.db_pass = app.config.get('DATABASE_PASS')
    if not app.db_pass:
        raise "DATABASE_PASS missing."
    app.db_name = app.config.get('DATABASE_NAME')
    if not app.db_name:
        raise "DATABASE_NAME missing."
    app.db_port = app.config.get('DATABASE_PORT')
    if not app.db_port:
        app.db_port = 3306

    # LDAP
    app.ldap_uri = app.config.get('LDAP_URI', '')
    if not app.ldap_uri:
        raise "LDAP_URI missing."
    app.ldap_root_bind_dn = app.config.get('LDAP_ROOT_BIND_DN', '')
    if not app.ldap_root_bind_dn:
        raise "LDAP_ROOT_BIND_DN missing."
    app.ldap_password = app.config.get('LDAP_PASSWORD', '')
    app.ldap_search_pattern = app.config.get('LDAP_SEARCH_PATTERN', '')
    if not app.ldap_search_pattern:
        raise "LDAP_SEARCH_PATTERN missing."
    app.ldap_search_base = app.config.get('LDAP_SEARCH_BASE', '')
    if not app.ldap_search_base:
        raise "LDAP_SEARCH_BASE missing."

    app.ldap_attr_email = app.config.get('LDAP_ATTR_EMAIL', '')
    if not app.ldap_attr_email:
        raise "LDAP_ATTR_EMAIL missing."
    app.ldap_attr_phone = app.config.get('LDAP_ATTR_PHONE', '')
    if not app.ldap_attr_phone:
        raise "LDAP_ATTR_PHONE missing."
    app.ldap_attr_username = app.config.get('LDAP_ATTR_USERNAME', '')
    if not app.ldap_attr_username:
        raise "LDAP_ATTR_USERNAME missing."
    app.ldap_attr_name = app.config.get('LDAP_ATTR_NAME', '')
    if not app.ldap_attr_name:
        raise "LLDAP_ATTR_NAME missing."
    app.ldap_attr_permission = app.config.get('LDAP_ATTR_PERMISSION', '')
    if not app.ldap_attr_permission:
        raise "LDAP_ATTR_PERMISSION missing."

    # email
    app.smtp_host = app.config.get('SMTP_HOST')
    if not app.smtp_host:
        raise "SMTP_HOST missing."
    app.smtp_user = app.config.get('SMTP_USER')
    if not app.smtp_user:
        raise "SMTP_USER missing."
    app.smtp_pass = app.config.get('SMTP_PASS')
    if not app.smtp_host:
        raise "SMTP_PASS missing."
    app.smtp_sender = app.config.get('SMTP_SENDER')
    if not app.smtp_sender:
        raise "SMTP_SENDER missing."
    app.smtp_mail_validation_template = app.config.get('SMTP_MAIL_VALIDATION_TEMPLATE')
    if not app.smtp_mail_validation_template:
        raise "SMTP_MAIL_VALIDATION_TEMPLATE' missing."
    app.smtp_mail_validation_subject = app.config.get('SMTP_MAIL_VALIDATION_SUBJECT', 'StarSSO Validation Code')
    app.smtp_mail_invitation_template = app.config.get('SMTP_MAIL_INVITATION_TEMPLATE')
    if not app.smtp_mail_invitation_template:
        raise "SMTP_MAIL_INVITATION_TEMPLATE missing."
    app.smtp_mail_invitation_subject = app.config.get('SMTP_MAIL_INVITATION_SUBJECT', 'StarSSO Invitation')

    # ???? wtf
    app.response_class = APIResponse
    app.request_class = APIRequest

    # session
    app.session_expiration = app.config.get('SESSION_EXPIRATION', '')
    if not app.session_expiration:
        raise "SESSION_EXPIRATION missing."
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(seconds=app.session_expiration)
    app.secret_key = app.config.get('SECRET_KEY', '')
    if not app.secret_key:
        raise "SECRET_KEY is missing."


def create_app():
    app = StarFlask(__name__)

    load_configuration(app)
    register_routes(app)
    register_db(app)
    register_services(app)

    @app.before_request
    def before_request():
        session.permanent = True
        if not request.parse():
            return -1

    @app.after_request
    def after_request(res):
        res.headers['Access-Control-Allow-Origin'] = 'http://localhost:8080'
        res.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        res.headers['Access-Control-Expose-Headers'] = '*'
        res.headers['Access-Control-Allow-Methods'] = '*'
        res.headers['Access-Control-Allow-Credentials'] = 'true'
        return res

    app.response_class = APIResponse
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
    app.json_encoder = MiniJSONEncoder

    @app.route('/')
    def index():
        return send_file('static/index.html')

    @app.route('/<path:filename>')
    def static_file(filename):
        return send_from_directory(app.static_folder, filename)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
