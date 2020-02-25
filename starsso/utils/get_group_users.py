# coding: utf-8
from ldap3 import Connection
from ldap_login import ad_admin_password,ad_admin_username,server
from get_user_info import get_user_info

def get_group_users(group_name):
    #返回组的用户
    user_list = []
    try:
        conn = Connection(server, auto_bind=True, user="sso\\"+ad_admin_username, password=ad_admin_password)
        conn.search(search_base=get_user_info(group_name).get('dn'),
                    search_filter= '(|(objectCategory=group)(objectCategory=user))',
                    search_scope='SUBTREE',
                    attributes=['starstudioMember', 'objectClass'],
                    size_limit=0   )
        for user in conn.entries[0].starstudioMember:
            user_list.append(user)
        return user_list

    except Exception as e:
        print(e)
        return None

    if __name__ =='__main__':
        print(get_group_users('组名'))
