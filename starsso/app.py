# coding: utf-8

from flask import Flask, jsonify, request, abort, g

from .utils import APIResponse, APIRequest

import ldap
import weakref
import os

from .admin import routes as admin_routes
from .user import routes as user_routes

def register_services(app):
    '''
        register_services() inserts common service methods.
    '''
    
    def get_ldap_connection():
        '''
            establish new ldap connection.
        '''
        l = ldap.initialize(app.ldap_uri)
        l.simple_bind_s(app.ldap_root_bind_dn, app.ldap_password)
        weakref.finalize(l, l.unbind_s) # prevent connection leaks.
        return l
    
    app.get_ldap_connection = get_ldap_connection
    

def register_routes(app):
    user_routes.register(app, url_prefix="/user")
    admin_routes.register(app, url_prefix="/admin")
    
    
def load_configuration(app):
    # session
    app.config.from_pyfile(os.environ.get('STARSSO_CONFIG_FILE', './config.py'))
    app.secret_key = app.config.get('SECRET_KEY', '')
    if not app.secret_key:
        raise "SECRET_KEY is missing."
    
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
    
    # ???? wtf
    app.response_class = APIResponse
    app.request_class = APIRequest
    
    
def get_wsgi_application():
    app = Flask(__name__)
    
    load_configuration(app)
    register_routes(app)
    register_services(app)

    return app

app = get_wsgi_application()
