from flask import Blueprint, request
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
    if email:
        pass
    if phone:
        pass
    return 0
