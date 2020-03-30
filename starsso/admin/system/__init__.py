from flask import Blueprint, request
from starsso.utils import check_param, check_login, UNKNOWN_ERROR, send_sms, SMS_FAILED, DUPLICATED_USERNAME, \
    send_email, check_admin

# for avoid same name ;)
bp = Blueprint('systemd', __name__, url_prefix='/system')


@bp.route('/add', methods=('GET', 'POST'))
@check_param
@check_login
@check_admin
def add():
    name = request.body['systemName']
    url = request.body['URL']
    users = request.body.get('users')
    system_id = 0
    return {"systemID": system_id}


@bp.route('/modify', methods=('GET', 'POST'))
@check_param
@check_login
@check_admin
def modify():
    system_id = request.body['ID']
    name = request.body.get('systemName')
    url = request.body.get('URL')
    users = request.body.get('users')
    return 0


@bp.route('/delete', methods=('GET', 'POST'))
@check_param
@check_login
@check_admin
def delete():
    system_id = request.body['ID']
    return 0


@bp.route('/get', methods=('GET', 'POST'))
@check_param
@check_login
@check_admin
def get():
    return []
