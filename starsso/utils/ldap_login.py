# coding: utf-8
from ldap3 import Server,ALL

ad_admin_username =''#管理员用户名
ad_admin_password=''#管理员密码

server=Server('ldap(s)://XXX.XX.XX.XX',get_info=ALL,use_ssl=True)


if __name__ =='__main__':
    pass