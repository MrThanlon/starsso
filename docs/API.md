# aStarSSO接口文档

如果不做说明，则响应内容为JSON格式的字符串，这种情况保证包含`code`字段表示状态码，以及`msg`字段为状态码含义，对于获取数据的接口，数据如果有则会放在`data`字段。

例如

```json
{
  "code": 0,
  "msg": "ok",
  "data": {
    ...
  }
}
```

为正常请求到的状态码。

如果不做说明，则支持GET/POST方式，POST可以使用的`Content-Type`有`form-data`/`x-www-urlencoded`/`json`，GET可以使用URL参数，推荐使用POST，包含文件的方式仅支持POST，`Content-Type`为`form`。如果没有说明请求参数，则不需要。

## 状态码

| `code` |        说明        |
| :----: | :----------------: |
|   0    |        正常        |
|   -1   |    请求参数错误    |
|   -2   |      重复登录      |
|  -11   |     邀请码错误     |
|  -23   |     登录名重复     |
|  -30   |     验证码错误     |
|  -33   | 未登录或cookie过期 |
|  -37   |  登录名或密码错误  |
|  -40   |    短信无法发送    |
|  -42   |   用户名已被注册   |
|  -51   |    非管理员用户    |
|  -100  |    后端未知错误    |

## 接口

### 用户 - `/user`

#### 登录 - `/user/login`

请求参数：

|  字段名  | 必填 |  类型  |  说明  |
| :------: | :--: | :----: | :----: |
| username |  是  | String | 登录名 |
| password |  是  | String |  密码  |

#### 登出 - `/user/logout`

#### 注册 - `/user/register`

请求参数：

|   字段名   | 必填 |  类型  |      说明      |
| :--------: | :--: | :----: | :------------: |
|  username  |  是  | String |     登录名     |
|  password  |  是  | String |      密码      |
|   email    |  是  | String | 注册的电子邮箱 |
| inviteCode |  是  | String |     邀请码     |

#### 查看个人信息 - `/user/profile`

返回数据：

|  字段名  | 必填 |  类型   |               说明               |
| :------: | :--: | :-----: | :------------------------------: |
| username |  是  | String  |              用户名              |
|  email   |  是  | String  |             电子邮箱             |
|  phone   |  是  | String  | 手机号，类型是String但只接受数字 |
|  admin   |  是  | Boolean |           是否为管理员           |

#### 请求验证码 - `/user/validationCode`

*注意：验证码仅用于修改个人信息*

| 字段名 | 必填 |  类型   |         说明         |
| :----: | :--: | :-----: | :------------------: |
| email  |  是  | Boolean | 是否通过电子邮件发送 |
| phone  |  是  | Boolean |   是否通过短信发送   |

#### 修改个人信息 - `/user/profile/modify`

*注意：在修改之前需要请求验证码*

请求参数：

|   字段名    | 必填 |  类型  |               说明               |
| :---------: | :--: | :----: | :------------------------------: |
|  password   |  是  | String |              原密码              |
| newPassword |  否  | String |              新密码              |
|    email    |  否  | String |             电子邮箱             |
|    phone    |  否  | String | 手机号，类型是String但只接受数字 |
|   verify    |  是  | Number |              验证码              |

#### 查看权限 - `/user/permission`

*注意：返回的数据是一个数组，每个元素的字段如下：*

|   字段名   | 必填 |  类型  |   说明   |
| :--------: | :--: | :----: | :------: |
|  systemID  |  是  | Number |  系统ID  |
| systemName |  是  | String | 系统名称 |
|    URL     |  是  | String |   链接   |

返回示例：

```json
{
  "code": 0,
  "msg": "ok",
  "data": [
    {
      "systemID": 1278,
      "systemName": "VPN",
      "URL": "https://vpn.starstudio.org/"
    },
    ...
  ]
}
```

### 管理 - `/admin`

#### 添加系统及分配权限 - `/admin/system/add`

*注意：如果有users参数，则必须使用`application/json`*

请求参数：

|   字段名   | 必填 |  类型  |      说明      |
| :--------: | :--: | :----: | :------------: |
| systemName |  是  | String |    系统名称    |
|    URL     |  是  | String |    系统名称    |
|   users    |  否  | Array  | 授权的用户列表 |

返回数据：

|  字段名  | 必填 |  类型  |  说明  |
| :------: | :--: | :----: | :----: |
| systemID |  是  | Number | 系统ID |

#### 修改系统及分配权限 - `/admin/system/modify`

*注意：如果有users参数，则必须使用`application/json`*

请求参数：

|   字段名   | 必填 |  类型  |      说明      |
| :--------: | :--: | :----: | :------------: |
|  systemID  |  是  | Number |     系统ID     |
| systemName |  否  | String |    系统名称    |
|    URL     |  否  | String |    系统链接    |
|   users    |  否  | Array  | 授权的用户列表 |

#### 删除系统 - `/admin/system/delete`

请求参数：

|  字段名  | 必填 |  类型  |  说明  |
| :------: | :--: | :----: | :----: |
| systemID |  是  | Number | 系统ID |

#### 查看系统权限分配 - `/admin/system/get`

*注意：返回的数据是一个数组，每个元素的字段如下：*

|   字段名   | 必填 |  类型  |          说明          |
| :--------: | :--: | :----: | :--------------------: |
|  systemID  |  是  | Number |         系统ID         |
| systemName |  是  | String |        系统名称        |
|    URL     |  是  | String |        系统链接        |
|   users    |  是  | Array  | 用户列表，元素为登录名 |

返回示例：

```json
{
  "code": 0,
  "msg": "ok",
  "data": [
    {
      "systemID": 127,
      "systemName": "VPN",
      "URL": "https://vpn.starstudio.org/"
      "users": [
        "abc@example.com",
        "efg@example.com"
      ]
    },
    {
      "systemID": 176,
      "systemName": "Graylog",
      "URL": "http://graylog.starstudio.org/",
      "users":[]
    },
    ...
  ]
}
```

#### 新用户邀请 - `/admin/user/invite`

请求参数：

| 字段名 | 必填 |  类型  |   说明   |
| :----: | :--: | :----: | :------: |
| email  |  否  | String | 电子邮箱 |
| phone  |  否  | String |  手机号  |

*注意：邮箱和手机号只填写一个，会发送邀请码和邀请链接*

#### 删除用户 - `/admin/user/delete`

请求参数：

|  字段名  | 必填 |  类型  |  说明  |
| :------: | :--: | :----: | :----: |
| username |  是  | String | 登录名 |

#### 修改用户信息 - `/admin/user/modify`

请求参数：

|  字段名  | 必填 |  类型  |   说明   |
| :------: | :--: | :----: | :------: |
| username |  是  | String |  登录名  |
| password |  否  | String |   密码   |
|  email   |  否  | String | 电子邮箱 |
|  phone   |  否  | String |  手机号  |

