# coding: utf-8
from ldap3 import Connection,AUTO_BIND_NO_TLS
from ldap_login import server,ad_admin_username,ad_admin_password


def get_user_info(username):

    try:
        #连接服务器
        conn=Connection( server, auto_bind=AUTO_BIND_NO_TLS, read_only=True, check_names=True, user="sso\\"+ad_admin_username, password=ad_admin_password)
        conn.search( search_base='', search_filter='', attributes=['blocked', 'permissionRoleName', 'studentNumber',  'wxID',  'qq'
 , 'fullName', 'registerTimestamp', 'registerYear',  'registerMonth','starstudioMember'])

        return {'dn' :conn.response[0]['dn']
                'blocked' : conn.response[0]['attributes']['blocked'],
                'permissionRoleName' :conn.response[0]['attributes']['permissionRoleName'],
                'studentNumber' : conn.response[0]['attributes']['studentNumber'],
                'wxID' : conn.response[0]['attributes']['wxID'],
                'qq' : conn.response[0]['attributes']['qq'],
                'fullName' : conn.response[0]['attributes']['fullName'],
                'registerTimestamp': conn.response[0]['attributes']['registerTimestamp'],
                'registerYear' : conn.response[0]['attributes']['registerYear'],
                'registerMonth': conn.response[0]['attributes']['registerMonth'],
                'starstudioMember': conn.response[0]['attributes']['starstudioMember'] }

    except Exception:
        return None

if __name__=='__main__':

    #测试
    print(get_user_info('用户名'))
    print(get_user_info('组名'))


