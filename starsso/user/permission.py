# coding: utf-8

from flask import Blueprint, session, current_app
from functools import reduce
import ldap
import ldap.filter

from starsso.utils import check_param, check_login, UNKNOWN_ERROR, send_sms, SMS_FAILED, DUPLICATED_USERNAME, \
    INVALID_USER, OK

bp = Blueprint('user_permission_api', __name__)


@bp.route("/permission", methods=('GET', 'POST'))
@check_param
@check_login
def permission():
    username = session['username']
    # FIXME: reused
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
    attrs = user_entry[1]
    ans = {x.decode('utf-8') for x in attrs.get(current_app.ldap_attr_permission)}
    systems = current_app.db.session.query(current_app.System).filter(
        current_app.db.or_(
            current_app.System.name.in_(ans),
            current_app.System.public == 1
        ))
    return [{'name': s.name, 'url': s.url, 'isGrant': s.name in ans} for s in systems]
