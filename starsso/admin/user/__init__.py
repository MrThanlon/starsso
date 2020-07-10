from flask import Blueprint, request, current_app
from starsso.utils import check_param, check_login, UNKNOWN_ERROR, send_sms, SMS_FAILED, DUPLICATED_USERNAME, \
    send_email, check_admin, INVALID_USER, INVALID_REQUEST, EXISTENT_EMAIL, validate_str, EMAIL_FAILED
import ldap
import ldap.filter
import random
import time
import config
import jwt

bp = Blueprint('system', __name__, url_prefix='/system')


@bp.route('/invite', methods=('POST', 'GET'))
@check_param
@check_login
@check_admin
def invite():
    email = request.body.get('email')
    phone = request.body.get('phone')
    # !XOR
    if (email and phone) or (not email and not phone):
        return INVALID_REQUEST
    l = current_app.get_ldap_connection()
    user_entries = l.search_s(current_app.ldap_search_base,
                              ldap.SCOPE_SUBTREE,
                              '(&(objectClass=person)(email={email}))'.format(
                                  email=ldap.filter.escape_filter_chars(email)))
    if user_entries:
        return EXISTENT_EMAIL
    # generate invite code
    # FIXME: not unique, it may cause crash, catch exception
    unique_code = random.randint(100000, 999999)
    code = jwt.encode({'email': email, 'code': unique_code, 'expire': time.time() + config.INVITE_EXPIRATION},
                      config.SECRET_KEY)
    current_app.Invite(unique_code).add()
    if email:
        if not send_email(email, code.decode('ascii'), email):
            current_app.looger.error('Failed to send email, {}, check configuration.'.format(email))
            return EMAIL_FAILED

    if phone:
        if not send_sms(phone, code.decode('ascii')):
            current_app.logger.error('Failed to send SMS, phone: {}, check configuration.'.format(phone))
            return SMS_FAILED
    return 0


@bp.route('/get', methods=('POST', 'GET'))
@check_param
@check_login
@check_admin
def get():
    l = current_app.get_ldap_connection()
    user_entries = l.search_s(current_app.ldap_search_base, ldap.SCOPE_SUBTREE, '(objectClass=person)')
    ans = [{
        'username': x[1][current_app.ldap_attr_username][0].decode('utf-8'),
        'fullName': x[1][current_app.ldap_attr_name][0].decode('utf-8') if current_app.ldap_attr_name in x[1] else None,
        'email': x[1][current_app.ldap_attr_email][0].decode('utf-8') if current_app.ldap_attr_email in x[1] else None,
        'admin':
            b'admin' in x[1][current_app.ldap_attr_permission] if current_app.ldap_attr_permission in x[1] else False
    } for x in user_entries]
    return ans


@bp.route('/delete', methods=('POST', 'GET'))
@check_param
@check_login
@check_admin
def delete():
    username = request.body['username']
    if not validate_str([username]):
        return INVALID_REQUEST
    l = current_app.get_ldap_connection()
    user_entries = l.search_s(current_app.ldap_search_base,
                              ldap.SCOPE_SUBTREE,
                              current_app.ldap_search_pattern.format(
                                  username=ldap.filter.escape_filter_chars(username)))
    if not user_entries:  # impossible?
        current_app.logger.info('deny modify request with username "{}". username not found.'.format(username))
        return INVALID_USER
    if len(user_entries) > 1:  # ambiguous username. not allow to login.
        current_app.logger.warn('ambiguous username "{}". login request is deined.'.format(username))
        return INVALID_USER, 'Duplicated users found. The users are blocked for security reason. Consult administrator to get help.'
    user_entry = user_entries[0]

    user_dn = user_entry[0]
    # FIXME: catch exception
    l.delete_s(user_dn)
    return 0


@bp.route('/modify', methods=('POST', 'GET'))
@check_param
@check_login
@check_admin
def modify():
    username = request.body['username']
    if not validate_str([username]):
        return INVALID_REQUEST
    password = request.body.get('password')
    phone = request.body.get('phone')
    full_name = request.body.get('fullName')
    admin = request.body.get('admin')

    l = current_app.get_ldap_connection()
    user_entries = l.search_s(current_app.ldap_search_base,
                              ldap.SCOPE_SUBTREE,
                              current_app.ldap_search_pattern.format(
                                  username=ldap.filter.escape_filter_chars(username)))
    if not user_entries:  # impossible?
        current_app.logger.info('deny modify request with username "{}". username not found.'.format(username))
        return INVALID_USER
    if len(user_entries) > 1:  # ambiguous username. not allow to login.
        current_app.logger.warn('ambiguous username "{}". login request is deined.'.format(username))
        return INVALID_USER, 'Duplicated users found. The users are blocked for security reason. Consult administrator to get help.'
    user_entry = user_entries[0]

    user_dn = user_entry[0]
    attrs = user_entry[1]
    # FIXME: catch exception
    modlist = []
    if password is not None:
        if not validate_str([password]):
            return INVALID_REQUEST
        l.passwd_s(user_dn, None, password.encode('ascii'))
    if full_name is not None:
        if not validate_str([full_name]):
            return INVALID_REQUEST
        modlist.append((ldap.MOD_REPLACE, current_app.ldap_attr_name, ldap.filter.escape_filter_chars(full_name).encode('utf-8')))
    if phone is not None:
        if not validate_str([phone]):
            return INVALID_REQUEST
        modlist.append((ldap.MOD_REPLACE, current_app.ldap_attr_phone, ldap.filter.escape_filter_chars(phone).encode('utf-8')))
    if admin is not None:
        if admin is True and (b'admin' not in attrs.get(current_app.ldap_attr_permission)):
            modlist.append((ldap.MOD_ADD, current_app.ldap_attr_permission, b'admin'))
        elif b'admin' in attrs.get(current_app.ldap_attr_permission):
            modlist.append((ldap.MOD_DELETE, current_app.ldap_attr_permission, b'admin'))
    if modlist:
        l.modify_s(user_dn, modlist)
    return 0
