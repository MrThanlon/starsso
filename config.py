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
DATABASE_HOST = '127.0.0.1'
DATABASE_USER = 'sso'
DATABASE_PASS = 'L1pFT497o2diNQci'
DATABASE_NAME = 'sso'

SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_COMMIT_TEARDOWN = True

# LDAP
LDAP_URI = 'ldap://47.103.204.9'
LDAP_ROOT_BIND_DN = 'cn=admin,dc=nodomain'
LDAP_PASSWORD = 'huangziyi.1970'
LDAP_SEARCH_PATTERN = '(&(objectClass=person)(cn={username}))'  # 一定要 escaped 和 validate ，小心注入
LDAP_SEARCH_BASE = 'ou=starstudio,dc=nodomain'

# SMTP
SMTP_HOST = 'smtp.qq.com'
SMTP_USER = '867945543@qq.com'
SMTP_PASS = 'kefcdpsowpgybbih'
SMTP_SENDER = '867945543@qq.com'
