# StarSSO接口文档

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

| `code` | 说明 |
| :----: | :--: |
|   0    | 正常 |
|        |      |
|        |      |

## 接口

### 用户 - `/user`

#### 登录 - `/user/login`

####修改个人信息 - `/user/modify`

#### 查看权限 - `/user/privilege/get`

### 管理 - `/admin`

#### 查看用户权限 - `/admin/privilege/get`

#### 修改用户权限 - `/admin/privilege/modify`

#### 新用户邀请 - `/admin/invite`