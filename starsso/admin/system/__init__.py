from flask import Blueprint, request, current_app
from starsso.utils import check_param, check_login, UNKNOWN_ERROR, send_sms, SMS_FAILED, DUPLICATED_USERNAME, \
    send_email, check_admin, NOT_EXISTENT_ID, INVALID_USER, INCLUDE_NON_EXISTENT_USERNAME, validate_str, INVALID_REQUEST

import ldap
import ldap.filter
from functools import reduce

# for avoid same name ;)
bp = Blueprint('systemd', __name__, url_prefix='/system')


@bp.route('/add', methods=('GET', 'POST'))
@check_param
@check_login
@check_admin
def add():
    name = request.body['name']
    url = request.body['url']
    public = request.body['public']
    public = 1 if public else 0
    if not validate_str([name, url]):
        return INVALID_REQUEST
    users = request.body.get('users')
    if users:
        l = current_app.get_ldap_connection()
        filter_str = '(&(objectClass=person)(|{}))'.format(
            reduce(lambda x, y: x + '(cn={})'.format(ldap.filter.escape_filter_chars(y)), users, ''))
        user_entries = l.search_s(current_app.ldap_search_base,
                                  ldap.SCOPE_SUBTREE,
                                  filter_str)
        if len(user_entries) != len(users):
            return INCLUDE_NON_EXISTENT_USERNAME
        dns = map(lambda x: x[0], user_entries)
        # add
        # FIXME: catch exception
        name_b = name.encode('utf-8')
        for dn in dns:
            l.modify_s(dn, [(ldap.MOD_ADD, 'permissionRoleName', name_b)])
    system = current_app.System(name, url, public)
    system.add()
    return 0


@bp.route('/modify', methods=('GET', 'POST'))
@check_param
@check_login
@check_admin
def modify():
    # FIXME: might not be used
    name = request.body['name']
    url = request.body.get('url')
    users = request.body.get('users')
    public = request.body.get('public')
    if not validate_str([name]):
        return INVALID_REQUEST
    system = current_app.db.session.query(current_app.System).filter_by(name=name).first()
    if not system:
        return NOT_EXISTENT_ID
    # FIXME: remove the user permission
    if users:
        l = current_app.get_ldap_connection()
        filter_str = '(&(objectClass=person)(|{}))'.format(
            reduce(lambda x, y: x + '(cn={})'.format(ldap.filter.escape_filter_chars(y)), users, ''))
        user_entries = l.search_s(current_app.ldap_search_base,
                                  ldap.SCOPE_SUBTREE,
                                  filter_str)
        if len(user_entries) != len(users):
            return INCLUDE_NON_EXISTENT_USERNAME
        dns = map(lambda x: x[0], user_entries)
        # modify
        # FIXME: catch exception
        name_b = system.name.encode('utf-8')
        for dn in dns:
            l.modify_s(dn, [(ldap.MOD_ADD, 'permissionRoleName', name_b)])

    if url != None:
        system.url = url
    if public != None:
        system.public = 1 if public else 0
    # FIXME: catch exception
    current_app.db.session.add(system)
    current_app.db.session.commit()
    return 0


@bp.route('/modifyPermission', methods=('GET', 'POST'))
@check_param
@check_login
@check_admin
def modify_permission():
    username = request.body['username']
    is_add = request.body['isAdd']
    name = request.body['name']
    system = current_app.db.session.query(current_app.System).filter_by(name=name).first()
    if not system:
        return NOT_EXISTENT_ID
    l = current_app.get_ldap_connection()
    user_entries = l.search_s(current_app.ldap_search_base,
                              ldap.SCOPE_SUBTREE,
                              current_app.ldap_search_pattern.format(
                                  username=ldap.filter.escape_filter_chars(username)))
    if not user_entries:  # user not found
        current_app.logger.info('deny login request with username "{}". username not found.'.format(username))
        return INVALID_USER
    if len(user_entries) > 1:  # ambiguous username. not allow to login.
        current_app.logger.warn('ambiguous username "{}". login request is deined.'.format(username))
        return INVALID_USER
    user_entry = user_entries[0]
    user_dn = user_entry[0]
    # FIXME: catch exception
    l.modify_s(user_dn, [(ldap.MOD_ADD if is_add else ldap.MOD_DELETE, 'permissionRoleName', name.encode('utf-8'))])
    return 0


@bp.route('/delete', methods=('GET', 'POST'))
@check_param
@check_login
@check_admin
def delete():
    name = request.body['name']
    system = current_app.db.session.query(current_app.System).filter_by(name=name).first()
    if not system:
        return NOT_EXISTENT_ID
    # FIXME: catch exception
    # remove from LDAP
    l = current_app.get_ldap_connection()
    user_entries = l.search_s(current_app.ldap_search_base, ldap.SCOPE_SUBTREE,
                              '(&(objectClass=person)(permissionRoleName={name}))'.format(
                                  name=ldap.filter.escape_filter_chars(system.name)))
    name_b = system.name.encode('utf-8')
    for u in user_entries:
        l.modify_s(u[0], [(ldap.MOD_DELETE, 'permissionRoleName', name_b)])
    current_app.db.session.delete(system)
    current_app.db.session.commit()
    return 0


@bp.route('/get', methods=('GET', 'POST'))
@check_param
@check_login
@check_admin
def get():
    systems = current_app.db.session.query(current_app.System).all()
    ans = []
    l = current_app.get_ldap_connection()
    for s in systems:
        user_entries = l.search_s(current_app.ldap_search_base,
                                  ldap.SCOPE_SUBTREE,
                                  '(&(objectClass=person)(permissionRoleName={system}))'.format(
                                      system=ldap.filter.escape_filter_chars(s.name)))
        users = list(map(lambda x: x[1]['cn'][0].decode('utf-8'), user_entries))
        ans.append({'name': s.name, 'url': s.url, 'users': users, 'public': s.public == 1})
    return ans
