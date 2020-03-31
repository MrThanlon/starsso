from flask import Blueprint, request, current_app
from starsso.utils import check_param, check_login, UNKNOWN_ERROR, send_sms, SMS_FAILED, DUPLICATED_USERNAME, \
    send_email, check_admin, NON_EXISTENT_ID, INVALID_USER, INCLUDE_NON_EXISTENT_USERNAME

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
    name = request.body['systemName']
    url = request.body['URL']
    users = request.body.get('users')
    if users:
        l = current_app.get_ldap_connection()
        filter_str = '(&(objectClass=person)(|{}))'.format(
            reduce(lambda x, y: x + '(cn={})'.format(y), users, ''))
        user_entries = l.search_s(current_app.ldap_search_base,
                                  ldap.SCOPE_SUBTREE,
                                  ldap.filter.escape_filter_chars(filter_str))
        if len(user_entries) != len(users):
            return INCLUDE_NON_EXISTENT_USERNAME
        dns = map(lambda x: x[0], user_entries)
        # add
        # FIXME: catch exception
        name_b = name.encode('utf-8')
        for dn in dns:
            l.modify_s(dn, [(ldap.MOD_ADD, 'permissionRoleName', name_b)])
    system = current_app.System(name, url)
    system.add()
    return {"systemID": system.ID}


@bp.route('/modify', methods=('GET', 'POST'))
@check_param
@check_login
@check_admin
def modify():
    system_id = request.body['systemID']
    url = request.body.get('URL')
    users = request.body.get('users')
    system = current_app.db.session.query(current_app.System).filter_by(ID=system_id).first()
    if not system:
        return NON_EXISTENT_ID
    if users:
        l = current_app.get_ldap_connection()
        filter_str = '(&(objectClass=person)(|{}))'.format(
            reduce(lambda x, y: x + '(cn={})'.format(y), users, ''))
        user_entries = l.search_s(current_app.ldap_search_base,
                                  ldap.SCOPE_SUBTREE,
                                  ldap.filter.escape_filter_chars(filter_str))
        if len(user_entries) != len(users):
            return INCLUDE_NON_EXISTENT_USERNAME
        dns = map(lambda x: x[0], user_entries)
        # modify
        # FIXME: catch exception
        name_b = system.name.encode('utf-8')
        for dn in dns:
            l.modify_s(dn, [(ldap.MOD_ADD, 'permissionRoleName', name_b)])

    if url:
        system.url = url
    # FIXME: catch exception
    current_app.db.session.add(system)
    current_app.db.session.commit()
    return 0


@bp.route('/delete', methods=('GET', 'POST'))
@check_param
@check_login
@check_admin
def delete():
    system_id = request.body['systemID']
    system = current_app.db.session.query(current_app.System).filter_by(ID=system_id).first()
    if not system:
        return NON_EXISTENT_ID
    # FIXME: catch exception
    # remove from LDAP
    l = current_app.get_ldap_connection()
    user_entries = l.search_s(current_app.ldap_search_base,
                              ldap.SCOPE_SUBTREE,
                              ldap.filter.escape_filter_chars(
                                  '(&(objectClass=person)(permissionRoleName={name}))'.format(name=system.name)
                              ))
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
                                  ldap.filter.escape_filter_chars(
                                      '(&(objectClass=person)(permissionRoleName={system}))'.format(system=s.name)
                                  ))
        users = list(map(lambda x: x[1]['cn'][0].decode('utf-8'), user_entries))
        ans.append({'systemID': s.ID, 'systemName': s.name, 'URL': s.url, 'users': users})
    return ans
