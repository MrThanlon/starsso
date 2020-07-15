from flask import Blueprint, session, current_app, request
import ldap
import ldap.filter
from starsso.utils import check_param, check_login, UNKNOWN_ERROR, send_sms, SMS_FAILED, DUPLICATED_USERNAME, \
    INVALID_USER, OK, check_admin, NOT_EXISTENT_ID

bp = Blueprint('admin_application_api', __name__)


@bp.route('/application', methods=('POST', 'GET'))
@check_param
@check_login
@check_admin
def application():
    applications = current_app.db.session.query(current_app.Application).all()
    return [{'applicationID': x.ID, 'username': x.username, 'systemName': x.name} for x in applications]


@bp.route('/application/operate', methods=('POST', 'GET'))
@check_param
@check_login
@check_admin
def application_operate():
    accept = request.body['accept']
    application_id = request.body['applicationID']
    app = current_app.db.session.query(current_app.Application).filter_by(ID=application_id).first()
    if not app:
        return NOT_EXISTENT_ID
    username = app.username
    system_name = app.name
    l = current_app.get_ldap_connection()
    user_entries = l.search_s(current_app.ldap_search_base,
                              ldap.SCOPE_SUBTREE,
                              current_app.ldap_search_pattern.format(
                                  username=ldap.filter.escape_filter_chars(username)))
    if not user_entries:  # user not found
        current_app.logger.info('deny application request with username "{}". username not found.'.format(username))
        return INVALID_USER
    if len(user_entries) > 1:  # ambiguous username. not allow to login.
        current_app.logger.warn('ambiguous username "{}". application request is deined.'.format(username))
        return INVALID_USER
    user_entry = user_entries[0]
    user_dn = user_entry[0]
    attrs = user_entry[1]
    system_name_b = system_name.encode('utf-8')
    if accept and (system_name_b not in attrs):
        # grant
        l.modify_s(user_dn, [(ldap.MOD_ADD, current_app.ldap_attr_permission, system_name_b)])

    current_app.db.session.delete(app)
    current_app.db.session.commit()
    return OK
