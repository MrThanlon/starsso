# coding: utf-8

# session secret
SECRET_KEY = b'4mMqW17KxjzckaLi/BQASN8m7KitzW4TQRFCtKgwrW3Z56Fs213C8PbK6m1wVm0a'

# session expiration, second
session_expiration = 864000

# database
database_host = '127.0.0.1'
database_user = 'starsso'
database_password = 'L1pFT497o2diNQci'
database_name = 'starsso'

# LDAP
LDAP_URI = 'ldap://xxx.xxx.xxx.xxx:xxx'
LDAP_ROOT_BIND_DN = 'cn=admin,dc=starstudio,dc=com'
LDAP_PASSWORD = ''
LDAP_SEARCH_PATTERN = '(&(objectClass=person)(cn={username}))' # 一定要 escaped 和 validate ，小心注入
LDAP_SEARCH_BASE = 'dc=starstudio,dc=com'