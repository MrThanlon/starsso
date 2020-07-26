# coding: utf-8

# session secret
SECRET_KEY = b'4mMqW17KxjzckaLi/BQASN8m7KitzW4TQRFCtKgwrW3Z56Fs213C8PbK6m1wVm0a'
# sig secret
HMAC_KEY = b'aYUhjnyaYUHjnmYUh87Y5676yweuhj6'
# JWE key
JWE_KEY = b'AhjhduhjYAUHHJf7hJAJ'
# session expiration, second
SESSION_EXPIRATION = 864000
# invite code expiration, second
INVITE_EXPIRATION = 604800
# validation code expiration, second
VALIDATION_EXPIRATION = 300

# database
DATABASE_HOST = '10.240.0.1'
DATABASE_USER = 'starsso'
DATABASE_PASS = 'dmPHDImheghJlrrT'
DATABASE_NAME = 'starsso'
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_COMMIT_TEARDOWN = True

# LDAP
LDAP_URI = 'ldap://10.240.5.3'
LDAP_ROOT_BIND_DN = 'cn=admin,dc=starstudio,dc=com'
LDAP_PASSWORD = ''
LDAP_SEARCH_PATTERN = '(&(objectClass=person)(cn={username}))'
LDAP_SEARCH_BASE = 'ou=gitlab2,dc=starstudio,dc=com'
LDAP_ATTR_EMAIL = 'postalAddress'
LDAP_ATTR_PHONE = 'telephoneNumber'
LDAP_ATTR_USERNAME = 'cn'
LDAP_ATTR_NAME = 'sn'
LDAP_ATTR_PERMISSION = 'permissionRoleName'

# SMTP
SMTP_HOST = 'smtp.qq.com'
SMTP_USER = '867945543@qq.com'
SMTP_PASS = 'kefcdpsowpgybbih'
SMTP_SENDER = '867945543@qq.com'
SMTP_MAIL_VALIDATION_TEMPLATE = 'Your validation code is {}, use it in 5m.'
SMTP_MAIL_VALIDATION_SUBJECT = 'StarSSO Validation Code'
SMTP_MAIL_INVITATION_TEMPLATE = 'Welcome to Star Studio! Register you account using the link down below\n'\
                                'https://example.com/register?invite={}'
SMTP_MAIL_INVITATION_SUBJECT = 'StarSSO Invitation'
