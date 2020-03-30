from flask import Blueprint, request, current_app
from starsso.utils import check_param, check_login, UNKNOWN_ERROR, send_sms, SMS_FAILED, DUPLICATED_USERNAME, \
    send_email, check_admin, INVALID_USER, INVALID_REQUEST
import ldap
import ldap.filter

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
    user_entries = l.search_s(current_app.ldap_search_base,
                              ldap.SCOPE_SUBTREE,
                              ldap.filter.escape_filter_chars(
                                  current_app.ldap_search_pattern.format(username=username)))
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
    password = request.body.get('password')
    email = request.body.get('email')
    phone = request.body.get('phone')
    full_name = request.body.get('fullName')
    admin = request.body.get('admin')
    l = current_app.get_ldap_connection()
    user_entries = l.search_s(current_app.ldap_search_base,
                              ldap.SCOPE_SUBTREE,
                              ldap.filter.escape_filter_chars(
                                  current_app.ldap_search_pattern.format(username=username)))
    if not user_entries:  # impossible?
        current_app.logger.info('deny modify request with username "{}". username not found.'.format(username))
        return INVALID_USER
    if len(user_entries) > 1:  # ambiguous username. not allow to login.
        current_app.logger.warn('ambiguous username "{}". login request is deined.'.format(username))
        return INVALID_USER, 'Duplicated users found. The users are blocked for security reason. Consult administrator to get help.'
    user_entry = user_entries[0]

    user_dn = user_entry[0]
    attrs = user_entries[1]
    # FIXME: catch exception
    modlist = []
    if password:
        l.passwd_s(user_dn, None, password.encode('ascii'))
    if full_name:
        modlist.append((ldap.MOD_REPLACE, 'fullName', full_name.encode('utf-8')))
    if email:
        modlist.append((ldap.MOD_REPLACE, 'email', email.encode('utf-8')))
    if phone:
        modlist.append((ldap.MOD_REPLACE, 'telephoneNumber', phone.encode('utf-8')))
    if admin:
        if admin == 'True' and ('admin' not in attrs.get('permissionRoleName')):
            modlist.append((ldap.MOD_ADD, 'permissionRoleName', b'admin'))
        elif 'admin' in attrs.get('permissionRoleName'):
            modlist.append((ldap.MOD_DELETE, 'permissionRoleName', b'admin'))
    if modlist:
        l.modify_s(user_dn, modlist)
    return 0
