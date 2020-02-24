# coding: utf-8
import random
import ldap

from flask import Blueprint, request, session, g, jsonify, current_app
from flask.views import MethodView
from wtforms import Form, StringField, validators

from starsso.utils import check_param, check_login
from starsso.common.response import make_api_response, OK, INVALID_REQUEST, INVALID_USER, ALREADY_LOGINED

bp = Blueprint('auth_api', __name__)


class Login(MethodView):
    
    class LoginForm(Form):
        username = StringField("username", validators=[validators.Email()])
        password = StringField("password")
        
    @property
    def logined(self):
        return len(self.current_user) > 0
    
    @property
    def current_user(self):
        return session.get('username', '')
    
    def get(self):
        '''
            Login.get sync login states.
        '''
        # validate login session.
        return make_api_response(code=OK, data={
            'username': self.current_user,
            'valid': self.logined
        })
        
    
    def post(self):
        '''
            Login.post provided sso web login API.
        '''
        if self.logined:
            return make_api_response(code=ALREADY_LOGINED)
        
        req = Login.LoginForm(request.form)
        if not req.validate():
            return make_api_response(code=INVALID_REQUEST), 400
        
        # search user to bind.
        l = current_app.get_ldap_connection()
        user_entries = l.search_s(current_app.ldap_search_base,
                 ldap.SCOPE_SUBTREE,
                 current_app.ldap_search_pattern.format(username=req.username.data))
        if not user_entries: # user not found
            return make_api_response(code=INVALID_USER)
        if len(user_entries) > 1: # ambigous username. not allow to login.
            return make_api_response(code=INVALID_USER,
                                     msg="Duplicated users found. The users are blocked for security reason. Consult administrator to get help.")
        user_entry = user_entries[0]
        
        # re-bind according to user dn.
        user_dn = user_entry[0]
        try:
            l.simple_bind_s(user_dn, req.password.data)
        except ldap.INVALID_CREDENTIALS:
            return make_api_response(code=INVALID_USER)
        
        # valid account. register session.
        session['username'] = req.username.data
        
        return make_api_response(code=OK, data={'user': req.username.data})
        
bp.add_url_rule('/login', view_func=Login.as_view("login"))


@bp.route("/validationCode", methods=('POST', 'GET'))
@check_param
@check_login
def validation_code():
    # generate code
    # FIXME: not secure, switch to random.org
    code = random.randint(100000, 999999)
    # send code via email or sms
    if request.body['email']:
        pass
    elif request.body['phone']:
        pass
    # set session
    session['code'] = code
    return 0


@bp.route("/register", methods=('POST', 'GET'))
@check_param
def register():
    # verify invite code
    pass
    # register!
    pass
    # set session
    return 0
