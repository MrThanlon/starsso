from flask import Blueprint, request, current_app
from starsso.utils import check_param, check_login, UNKNOWN_ERROR, send_sms, SMS_FAILED, DUPLICATED_USERNAME, \
    send_email, check_admin

bp = Blueprint('system', __name__, url_prefix='/system')


@bp.route('/invite', methods=('POST', 'GET'))
@check_param
@check_login
@check_admin
def invite():
    email = request.body.get('email')
    phone = request.body.get('phone')
    l = current_app.get_ldap_connection()
    # TODO: invite
    if email:
        pass
    if phone:
        pass
    return 0


@bp.route('/delete', methods=('POST', 'GET'))
@check_param
@check_login
@check_admin
def delete():
    username = request.body['username']
    l = current_app.get_ldap_connection()
    # TODO: set blocked
    return 0


@bp.route('/modify', methods=('POST', 'GET'))
@check_param
@check_login
@check_admin
def modify():
    username = request.body['username']
    password = request.body.get('password')
    email = request.body.get('email')
    phone = request.body.get('phone')
    admin = request.body.get('admin')
    l = current_app.get_ldap_connection()
    # TODO: modify
    if password:
        pass
    if email:
        pass
    if phone:
        pass
    if admin:
        pass
    return 0
