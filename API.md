# 硅谷甄选后台管理系统 · 接口文档

> 供前端对接使用。本文档基于后端源码（router / controller / model）整理，与线上行为一致。

## 1. 概述

| 项目 | 说明 |
| --- | --- |
| 服务地址 | `http://127.0.0.1:10086`（前端本地开发可通过 `VITE_APP_BASE_API = '/api'` 代理） |
| 接口风格 | RESTful，数据格式统一为 JSON（文件上传除外） |
| 测试账号 | `admin` / `111111` |
| Swagger | `http://127.0.0.1:10086/swagger/index.html` |
| 静态资源 | 图片通过 `/static/...` 路径访问，上传后返回的 URL 已带 `/api` 前缀 |

## 2. 通用约定（前端必读）

### 2.1 认证方式

- 除 **登录**、**登出** 两个接口外，其余所有接口都需要登录。
- Token 放在**请求头 `Token`** 中传递（注意：不是 `Authorization: Bearer xxx`）。

```
Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

- Token 缺失返回 `code=207`（需要登录）；Token 无效/过期返回 `code=206`（无效的 Token），此时应引导用户重新登录。
- `<el-upload>` 组件上传文件时，需通过 `headers` 属性携带 `Token` 请求头。

### 2.2 统一响应格式

无论成功失败，**HTTP 状态码均为 200**，业务是否成功需判断 `code` 字段：

```json
{
  "code": 200,
  "message": "success",
  "data": {},
  "ok": true
}
```

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| code | number | 业务状态码，200 表示成功 |
| message | string | 提示信息 |
| data | any | 业务数据，无数据时为 `null` |
| ok | boolean | 是否成功 |

**下文每个接口只描述 `data` 的结构与可能返回的错误码，不再重复外层包裹。**

### 2.3 业务状态码表

| code | 含义 | 说明 |
| --- | --- | --- |
| 200 | 成功 | |
| 201 | 请求参数错误 | 参数缺失、格式不正确等 |
| 202 | 用户名已存在 | 新增用户时 |
| 203 | 用户名不存在 | 登录时 |
| 204 | 用户名或密码错误 | 登录时 |
| 205 | 服务繁忙 | 服务内部错误 |
| 206 | 无效的 Token | Token 解析失败，需重新登录 |
| 207 | 需要登录 | 未携带 Token |
| 208 | 该节点下有子节点，不可以删除 | 删除菜单时 |
| 209 | 请求路径不存在 | 接口地址错误 |

### 2.4 通用说明

- **分页**：分页参数 `page`（页码，从 1 开始）、`limit`（每页条数）均为**路径参数**，如 `/1/10`；传非法值时后端按 `page=1`、`limit=10` 兜底。
- **分页响应统一结构**（下称"分页结构"）：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| records | array | 当前页数据列表 |
| total | number | 总记录数 |
| size | number | 每页条数 |
| current | number | 当前页码 |
| pages | number | 总页数 |
| searchCount | boolean | 是否统计总数（部分接口返回） |

- **时间格式**：`yyyy-MM-dd HH:mm:ss`，如 `"2024-09-08 10:30:00"`。
- **ID 精度提醒**：所有 ID 由雪花算法生成，是 64 位整数，可能超出 JS `Number.MAX_SAFE_INTEGER`。建议前端使用 `json-bigint` 解析响应，避免精度丢失。
- **冗余字段**：部分实体响应中可能携带 `ID`、`createTime`、`updateTime` 等字段，属于通用模型字段，业务上请使用对应的业务 `id`。

---

## 3. 登录认证

### 3.1 用户登录

`POST /admin/acl/index/login` ｜ 无需 Token

**请求参数（Body）**

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| username | string | 是 | 用户名 |
| password | string | 是 | 密码 |

**请求示例**

```json
{
  "username": "admin",
  "password": "111111"
}
```

**响应 data**：`string`，JWT Token 字符串

```json
{
  "code": 200,
  "message": "success",
  "data": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "ok": true
}
```

**可能错误码**：201 参数错误；203 用户名不存在；204 用户名或密码错误

### 3.2 用户登出

`POST /admin/acl/index/logout` ｜ 无需 Token

**请求参数**：无

**响应 data**：`null`

> 登出为无状态实现，服务端不使 Token 失效，前端清除本地 Token 即可。

---

## 4. 用户信息

### 4.1 获取登录用户信息

`GET /admin/acl/index/info` ｜ 需要 Token

**请求参数**：无（后端从 Token 中解析用户）

**响应 data**

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| routes | string[] | 用户可访问的路由权限 code 列表 |
| buttons | string[] | 用户拥有的按钮权限 code 列表 |
| roles | string[] | 用户角色名列表 |
| name | string | 用户名 |
| avatar | string | 头像 URL |

**响应示例**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "routes": ["Acl", "Sku", "Spu", "Trademark"],
    "buttons": ["btn.User.add", "btn.Trademark.add"],
    "roles": ["系统管理员"],
    "name": "admin",
    "avatar": "http://xxx.com/avatar.png"
  },
  "ok": true
}
```

---

## 5. 用户管理

### 5.1 新增用户

`POST /admin/acl/user/save` ｜ 需要 Token

**请求参数（Body）**

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| username | string | 是 | 登录用户名，唯一 |
| name | string | 是 | 用户昵称 |
| password | string | 是 | 登录密码 |

**响应 data**：`null`

**可能错误码**：201 参数错误；202 用户名已存在；205 服务繁忙

### 5.2 获取用户分页列表

`GET /admin/acl/user/{page}/{limit}` ｜ 需要 Token

**请求参数**

| 位置 | 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| Path | page | number | 是 | 页码，从 1 开始 |
| Path | limit | number | 是 | 每页条数 |
| Query | username | string | 否 | 按用户名模糊搜索 |

**请求示例**：`GET /admin/acl/user/1/10?username=admin`

**响应 data**：分页结构，`records` 元素结构如下

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | number | 用户 ID |
| username | string | 用户名 |
| roleName | string | 角色名（多个以逗号分隔，未分配为空） |
| name | string | 昵称 |
| phone | string | 手机号 |
| password | string | 密码 |
| createTime | string | 创建时间 |
| updateTime | string | 更新时间 |

### 5.3 更新用户

`PUT /admin/acl/user/update` ｜ 需要 Token

**请求参数（Body）**

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| id | number | 是 | 用户 ID |
| username | string | 是 | 用户名 |
| name | string | 是 | 昵称 |

**响应 data**：`null`

**可能错误码**：201 参数错误；205 服务繁忙

### 5.4 删除用户

`DELETE /admin/acl/user/remove/{id}` ｜ 需要 Token

**请求参数**

| 位置 | 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| Path | id | number | 是 | 用户 ID |

**响应 data**：`null`

### 5.5 批量删除用户

`DELETE /admin/acl/user/batchRemove` ｜ 需要 Token

**请求参数（Body）**：用户 ID 数组（JSON 数组，不能为空）

```json
[1234567890123456789, 1234567890123456790]
```

**响应 data**：`null`

**可能错误码**：201 参数错误（数组为空或格式错误）；205 服务繁忙

### 5.6 获取用户已分配角色

`GET /admin/acl/user/toAssign/{adminId}` ｜ 需要 Token

**请求参数**

| 位置 | 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| Path | adminId | number | 是 | 用户 ID |

**响应 data**

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| assignRoles | Role[] | 该用户已分配的角色 |
| allRolesList | Role[] | 系统中全部角色 |

**Role 结构**

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | number | 角色 ID |
| roleName | string | 角色名 |
| remark | string | 备注 |
| createTime | string | 创建时间 |

### 5.7 为用户分配角色

`POST /admin/acl/user/doAssignRole` ｜ 需要 Token

> 全量覆盖：提交的角色列表即该用户最终的角色。

**请求参数（Body）**

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| userId | number | 是 | 用户 ID |
| roleIdList | number[] | 是 | 角色 ID 列表（可为空数组，表示清空角色） |

**请求示例**

```json
{
  "userId": 1234567890123456789,
  "roleIdList": [1, 2]
}
```

**响应 data**：`null`

---

## 6. 角色管理

### 6.1 获取角色分页列表

`GET /admin/acl/role/{page}/{limit}` ｜ 需要 Token

**请求参数**

| 位置 | 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| Path | page | number | 是 | 页码，从 1 开始 |
| Path | limit | number | 是 | 每页条数 |
| Query | roleName | string | 否 | 按角色名模糊搜索 |

**响应 data**：分页结构，`records` 元素为 [Role 结构](#56-获取用户已分配角色)（id、roleName、remark、createTime）

### 6.2 新增角色

`POST /admin/acl/role/save` ｜ 需要 Token

**请求参数（Body）**

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| roleName | string | 是 | 角色名 |
| remark | string | 否 | 备注 |

**响应 data**：`null`

### 6.3 更新角色

`PUT /admin/acl/role/update` ｜ 需要 Token

**请求参数（Body）**

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| id | number | 是 | 角色 ID |
| roleName | string | 是 | 角色名 |
| remark | string | 否 | 备注 |

**响应 data**：`null`

### 6.4 删除角色

`DELETE /admin/acl/role/remove/{id}` ｜ 需要 Token

**请求参数**

| 位置 | 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| Path | id | number | 是 | 角色 ID |

**响应 data**：`null`

---

## 7. 权限（菜单）管理

### 7.1 获取菜单列表

`GET /admin/acl/permission` ｜ 需要 Token

**请求参数**：无

**响应 data**：树形菜单数组，节点结构如下

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | number | 菜单 ID |
| name | string | 菜单名称 |
| pid | number | 父级菜单 ID（一级菜单为 0） |
| code | string | 权限 code（路由名 / 按钮名） |
| toCode | string | 跳转 code |
| type | number | 类型：1 路由节点（目录/菜单），2 功能按钮（挂在第 4 级）；线上数据实测无 type=3，路由/按钮之分由 level 决定 |
| status | string | 状态 |
| level | number | 层级：1~3 为路由，4 为按钮 |
| children | Menu[] | 子菜单数组 |
| select | boolean | 是否被勾选（角色分配权限时用） |

### 7.2 新增菜单

`POST /admin/acl/permission/save` ｜ 需要 Token

**请求参数（Body）**

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| name | string | 是 | 菜单名称（不能与已有菜单重复） |
| pid | number | 是 | 父级菜单 ID，一级菜单传 0 |
| code | string | 是 | 权限 code |
| type | number | 是 | 类型：1 路由节点（目录/菜单），2 功能按钮；按钮节点须配 level=4 |
| level | number | 是 | 层级：1~3 为路由，4 为按钮 |

**响应 data**：`null`

### 7.3 更新菜单

`PUT /admin/acl/permission/update` ｜ 需要 Token

**请求参数（Body）**

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| id | number | 是 | 菜单 ID |
| name | string | 是 | 菜单名称 |
| pid | number | 是 | 父级菜单 ID |
| code | string | 是 | 权限 code |
| level | number | 是 | 层级 |

**响应 data**：`null`

### 7.4 删除菜单

`DELETE /admin/acl/permission/remove/{id}` ｜ 需要 Token

**请求参数**

| 位置 | 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| Path | id | number | 是 | 菜单 ID |

**响应 data**：`null`

**可能错误码**：208 该节点下有子节点，不可以删除（需先删除子节点）

### 7.5 根据角色获取菜单（回显权限树）

`GET /admin/acl/permission/toAssign/{roleId}` ｜ 需要 Token

**请求参数**

| 位置 | 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| Path | roleId | number | 是 | 角色 ID |

**响应 data**：全量菜单树（同 7.1 结构），该角色已拥有的节点 `select` 为 `true`，前端据此回显勾选状态。

### 7.6 给角色分配权限

`POST /admin/acl/permission/doAssign` ｜ 需要 Token

> **注意：参数通过 URL Query 传递，不是 JSON Body！**
> 全量覆盖：提交的菜单 ID 列表即该角色最终拥有的权限。

**请求参数**

| 位置 | 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| Query | roleId | number | 是 | 角色 ID |
| Query | permissionId | string | 是 | 菜单 ID 列表，多个用英文逗号分隔 |

**请求示例**

```
POST /admin/acl/permission/doAssign?roleId=1&permissionId=1,2,3,4,5
```

**响应 data**：`null`

---

## 8. 文件上传

### 8.1 上传图片

`POST /admin/product/fileUpload` ｜ 需要 Token

**请求参数（multipart/form-data）**

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| file | file | 是 | 图片文件 |

**curl 示例**

```bash
curl -X POST 'http://127.0.0.1:10086/admin/product/fileUpload' \
  -H 'Token: <你的Token>' \
  -F 'file=@./logo.png'
```

**响应 data**：`string`，图片访问 URL

```json
{
  "code": 200,
  "message": "success",
  "data": "/api/static/img/sph/20240908/logo.png",
  "ok": true
}
```

> 返回的 URL 以 `/api` 开头，前端直接拼接 `VITE_APP_BASE_API` 代理使用即可；图片按上传日期归档到不同目录。

---

## 9. 品牌管理

### 9.1 获取品牌分页列表

`GET /admin/product/baseTrademark/{page}/{limit}` ｜ 需要 Token

**请求参数**

| 位置 | 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| Path | page | number | 是 | 页码，从 1 开始 |
| Path | limit | number | 是 | 每页条数 |

**响应 data**：分页结构，`records` 元素结构如下

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | number | 品牌 ID |
| tmName | string | 品牌名称 |
| logoUrl | string | 品牌 LOGO 图片 URL |
| createTime | string | 创建时间 |

### 9.2 新增品牌

`POST /admin/product/baseTrademark/save` ｜ 需要 Token

**请求参数（Body）**

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| tmName | string | 是 | 品牌名称 |
| logoUrl | string | 是 | LOGO 图片 URL（先调 8.1 上传获得） |

**响应 data**：`null`

### 9.3 更新品牌

`PUT /admin/product/baseTrademark/update` ｜ 需要 Token

**请求参数（Body）**

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| id | number | 是 | 品牌 ID |
| tmName | string | 是 | 品牌名称 |
| logoUrl | string | 是 | LOGO 图片 URL |

**响应 data**：`null`

### 9.4 删除品牌

`DELETE /admin/product/baseTrademark/remove/{id}` ｜ 需要 Token

**请求参数**

| 位置 | 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| Path | id | number | 是 | 品牌 ID |

**响应 data**：`null`

### 9.5 获取所有品牌（不分页）

`GET /admin/product/baseTrademark/getTrademarkList` ｜ 需要 Token

**请求参数**：无

**响应 data**：品牌数组，元素结构同 9.1 的 `records`（id、tmName、logoUrl）

---

## 10. 商品分类

> 分类为三级结构：一级分类 → 二级分类 → 三级分类。选择上级分类后，用其 `id` 查询下一级。

### 10.1 获取一级分类

`GET /admin/product/getCategory1` ｜ 需要 Token

**请求参数**：无

**响应 data**

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | number | 一级分类 ID |
| name | string | 分类名称 |

### 10.2 获取二级分类

`GET /admin/product/getCategory2/{id}` ｜ 需要 Token

**请求参数**

| 位置 | 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| Path | id | number | 是 | 一级分类 ID |

**响应 data**

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | number | 二级分类 ID |
| name | string | 分类名称 |
| category1Id | number | 所属一级分类 ID |

### 10.3 获取三级分类

`GET /admin/product/getCategory3/{id}` ｜ 需要 Token

**请求参数**

| 位置 | 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| Path | id | number | 是 | 二级分类 ID |

**响应 data**

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | number | 三级分类 ID |
| name | string | 分类名称 |
| category2Id | number | 所属二级分类 ID |

---

## 11. 平台属性管理

### 11.1 获取分类下已有的属性与属性值

`GET /admin/product/attrInfoList/{c1Id}/{c2Id}/{c3Id}` ｜ 需要 Token

**请求参数**

| 位置 | 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| Path | c1Id | number | 是 | 一级分类 ID |
| Path | c2Id | number | 是 | 二级分类 ID |
| Path | c3Id | number | 是 | 三级分类 ID |

**响应 data**：属性数组，元素结构如下

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | number | 属性 ID |
| attrName | string | 属性名（如"颜色"） |
| categoryId | number | 所属三级分类 ID |
| categoryLevel | number | 分类级别（固定 3） |
| attrValueList | AttrValue[] | 属性值列表 |

**AttrValue 结构**

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | number | 属性值 ID |
| valueName | string | 属性值名称（如"红色"） |
| attrId | number | 所属属性 ID |

**响应示例**

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "attrName": "颜色",
      "categoryId": 61,
      "categoryLevel": 3,
      "attrValueList": [
        { "id": 1, "valueName": "红色", "attrId": 1 },
        { "id": 2, "valueName": "蓝色", "attrId": 1 }
      ]
    }
  ],
  "ok": true
}
```

### 11.2 保存属性（新增或修改）

`POST /admin/product/saveAttrInfo` ｜ 需要 Token

> **一个接口两用：`id` 不传或为 0 时新增；携带 `id` 时修改（整体覆盖该属性及属性值）。**

**请求参数（Body）**

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| id | number | 否 | 属性 ID，修改时必传 |
| attrName | string | 是 | 属性名 |
| categoryId | number | 是 | 三级分类 ID |
| categoryLevel | number | 是 | 分类级别（传 3） |
| attrValueList | array | 否 | 属性值列表 |

`attrValueList` 元素结构：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| valueName | string | 是 | 属性值名称 |
| id | number | 否 | 属性值 ID（新增时可不传） |

**请求示例**

```json
{
  "attrName": "颜色",
  "categoryId": 61,
  "categoryLevel": 3,
  "attrValueList": [
    { "valueName": "红色" },
    { "valueName": "蓝色" }
  ]
}
```

**响应 data**：`null`

### 11.3 删除属性

`DELETE /admin/product/deleteAttr/{attrId}` ｜ 需要 Token

**请求参数**

| 位置 | 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| Path | attrId | number | 是 | 属性 ID |

**响应 data**：`null`

---

## 12. SPU 管理

### 12.1 获取 SPU 分页列表

`GET /admin/product/{page}/{limit}` ｜ 需要 Token

**请求参数**

| 位置 | 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| Path | page | number | 是 | 页码，从 1 开始 |
| Path | limit | number | 是 | 每页条数 |
| Query | category3Id | number | 是 | 三级分类 ID（**必传**，否则报参数错误） |

**请求示例**：`GET /admin/product/1/10?category3Id=61`

> 后端同时兼容旧路径 `GET /admin/product/spu/list?page=&size=&category3Id=`（分页走 Query，参数名 `size`/`limit` 均可），两条路由并存且返回一致；新对接请优先使用上方路径参数风格。

**响应 data**：分页结构，`records` 元素结构如下

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | number | SPU ID |
| spuName | string | SPU 名称 |
| description | string | SPU 描述 |
| category3Id | number | 三级分类 ID |
| tmId | number | 品牌 ID |
| createTime | string | 创建时间 |
| updateTime | string | 更新时间 |

### 12.2 新增 SPU

`POST /admin/product/saveSpuInfo` ｜ 需要 Token

**请求参数（Body）**

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| spuName | string | 是 | SPU 名称 |
| description | string | 否 | SPU 描述 |
| category3Id | number | 是 | 三级分类 ID |
| tmId | number | 是 | 品牌 ID |
| spuImageList | SpuImage[] | 否 | 图片列表 |
| spuSaleAttrList | SpuSaleAttr[] | 否 | 销售属性列表 |

> `id`、`spuId`、`createTime`、`updateTime` 等由服务端生成，**前端无需传递**（传了也会被覆盖）。

`spuImageList` 元素结构：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| imgName | string | 是 | 图片名称 |
| imgUrl | string | 是 | 图片 URL（先调 8.1 上传获得） |

`spuSaleAttrList` 元素结构：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| baseSaleAttrId | number | 是 | 基础销售属性 ID（从 12.5 获取） |
| saleAttrName | string | 是 | 销售属性名称（如"颜色"） |
| spuSaleAttrValueList | array | 否 | 销售属性值列表 |

`spuSaleAttrValueList` 元素结构：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| saleAttrValueName | string | 是 | 属性值名称（如"黑色"） |
| baseSaleAttrId | number | 是 | 所属基础销售属性 ID |

**请求示例**

```json
{
  "spuName": "华为 Mate70",
  "description": "旗舰手机",
  "category3Id": 61,
  "tmId": 1,
  "spuImageList": [
    { "imgName": "meta70.jpg", "imgUrl": "/api/static/img/sph/20241210/meta70.jpg" }
  ],
  "spuSaleAttrList": [
    {
      "baseSaleAttrId": 1,
      "saleAttrName": "颜色",
      "spuSaleAttrValueList": [
        { "saleAttrValueName": "黑色", "baseSaleAttrId": 1 },
        { "saleAttrValueName": "白色", "baseSaleAttrId": 1 }
      ]
    }
  ]
}
```

**响应 data**：`null`

### 12.3 更新 SPU

`POST /admin/product/updateSpuInfo` ｜ 需要 Token

**请求参数（Body）**：与 12.2 新增一致，另需携带：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| id | number | 是 | SPU ID |

> 更新为整体覆盖：图片列表、销售属性以本次提交为准，旧的会被删除后重建。

**响应 data**：`null`

### 12.4 删除 SPU

`DELETE /admin/product/deleteSpu/{id}` ｜ 需要 Token

**请求参数**

| 位置 | 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| Path | id | number | 是 | SPU ID |

**响应 data**：`null`

### 12.5 获取全部销售属性

`GET /admin/product/baseSaleAttrList` ｜ 需要 Token

**请求参数**：无

**响应 data**

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | number | 基础销售属性 ID |
| name | string | 销售属性名称（如"颜色""版本"） |

**响应示例**

```json
{
  "code": 200,
  "message": "success",
  "data": [
    { "id": 1, "name": "颜色" },
    { "id": 2, "name": "版本" }
  ],
  "ok": true
}
```

---

## 13. SKU 管理

### 13.1 获取 SPU 图片列表

`GET /admin/product/spuImageList/{id}` ｜ 需要 Token

**请求参数**

| 位置 | 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| Path | id | number | 是 | SPU ID |

**响应 data**

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | number | 图片 ID |
| imgName | string | 图片名称 |
| imgUrl | string | 图片 URL |
| spuId | number | 所属 SPU ID |

### 13.2 获取 SPU 销售属性列表

`GET /admin/product/spuSaleAttrList/{id}` ｜ 需要 Token

**请求参数**

| 位置 | 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| Path | id | number | 是 | SPU ID |

**响应 data**：销售属性数组，元素结构如下

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | number | 记录 ID |
| baseSaleAttrId | number | 基础销售属性 ID |
| saleAttrName | string | 销售属性名称 |
| spuId | number | 所属 SPU ID |
| spuSaleAttrValueList | array | 属性值列表 |

`spuSaleAttrValueList` 元素结构：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | number | 属性值 ID |
| saleAttrValueName | string | 属性值名称 |
| baseSaleAttrId | number | 基础销售属性 ID |
| spuId | number | 所属 SPU ID |

**响应示例**

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "baseSaleAttrId": 1,
      "saleAttrName": "颜色",
      "spuId": 1,
      "spuSaleAttrValueList": [
        { "id": 1, "saleAttrValueName": "黑色", "baseSaleAttrId": 1, "spuId": 1 }
      ]
    }
  ],
  "ok": true
}
```

### 13.3 新增 SKU

`POST /admin/product/saveSkuInfo` ｜ 需要 Token

**请求参数（Body）**

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| spuID | number | 是 | 所属 SPU ID（注意字段名为 `spuID`） |
| category3Id | number | 是 | 三级分类 ID |
| tmId | number | 是 | 品牌 ID |
| skuName | string | 是 | SKU 名称 |
| price | number | 是 | 价格（单位：分） |
| weight | number | 否 | 重量（单位：克） |
| skuDesc | string | 否 | SKU 描述 |
| skuDefaultImg | string | 是 | 默认展示图片 URL |
| isSale | number | 否 | 上架状态：0 下架（默认）、1 上架 |
| skuAttrValueList | array | 否 | 平台属性列表 |
| skuSaleAttrValueList | array | 否 | 销售属性值列表 |
| skuImageList | array | 否 | 图片列表 |

> `id`、`skuId` 等由服务端生成，无需传递。`price`、`weight`、各 ID 字段兼容数字或字符串。

`skuAttrValueList` 元素结构（平台属性，从 11.1 获取）：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| attrId | number | 是 | 平台属性 ID |
| valueId | number | 是 | 平台属性值 ID |
| valueName | string | 是 | 属性值名称 |
| attrName | string | 是 | 属性名称 |

`skuSaleAttrValueList` 元素结构（销售属性，从 13.2 获取）：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| saleAttrId | number | 是 | 销售属性 ID |
| saleAttrValueId | number | 是 | 销售属性值 ID |
| saleAttrName | string | 是 | 销售属性名称 |
| saleAttrValueName | string | 是 | 销售属性值名称 |

`skuImageList` 元素结构（图片，从 13.1 获取）：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| imgName | string | 是 | 图片名称 |
| imgUrl | string | 是 | 图片 URL |
| spuImgId | number | 否 | SPU 图片 ID |
| isDefault | string | 否 | 是否默认图："1" 是、"0" 否 |

**请求示例**

```json
{
  "spuID": 1,
  "category3Id": 61,
  "tmId": 1,
  "skuName": "华为 Mate70 黑色 12+256",
  "price": 599900,
  "weight": 209,
  "skuDesc": "黑色 12+256",
  "skuDefaultImg": "/api/static/img/sph/20241210/meta70.jpg",
  "isSale": 0,
  "skuAttrValueList": [
    { "attrId": 1, "valueId": 1, "valueName": "红色", "attrName": "颜色" }
  ],
  "skuSaleAttrValueList": [
    { "saleAttrId": 1, "saleAttrValueId": 1, "saleAttrName": "颜色", "saleAttrValueName": "黑色" }
  ],
  "skuImageList": [
    { "imgName": "meta70.jpg", "imgUrl": "/api/static/img/sph/20241210/meta70.jpg", "spuImgId": 1, "isDefault": "1" }
  ]
}
```

**响应 data**：`null`

### 13.4 根据 SPU 查询 SKU 列表

`GET /admin/product/findBySpuId/{id}` ｜ 需要 Token

**请求参数**

| 位置 | 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| Path | id | number | 是 | SPU ID |

**响应 data**：13.6 SKU 详情结构的数组

### 13.5 获取 SKU 分页列表

`GET /admin/product/list/{page}/{limit}` ｜ 需要 Token

**请求参数**

| 位置 | 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| Path | page | number | 是 | 页码，从 1 开始 |
| Path | limit | number | 是 | 每页条数 |
| Query | spuId | number | 否 | 按所属 SPU 过滤（实测有效） |

**响应 data**：分页结构，`records` 元素为 13.6 SKU 详情结构。
注意：列表接口返回的 `skuAttrValueList` / `skuSaleAttrValueList` / `skuImageList` 恒为 `null`（非空数组），需要完整嵌套数据请走 13.6 详情接口。

### 13.6 获取 SKU 详情

`GET /admin/product/getSkuInfo/{id}` ｜ 需要 Token

**请求参数**

| 位置 | 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| Path | id | number | 是 | SKU ID |

**响应 data**

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | number | SKU ID |
| spuID | number | 所属 SPU ID |
| category3Id | number | 三级分类 ID |
| tmId | number | 品牌 ID |
| skuName | string | SKU 名称 |
| price | number | 价格（单位：分） |
| weight | number | 重量（单位：克） |
| skuDesc | string | SKU 描述 |
| skuDefaultImg | string | 默认图片 URL |
| isSale | number | 上架状态：0 下架、1 上架 |
| createTime | string | 创建时间 |
| updateTime | string | 更新时间 |
| skuAttrValueList | array | 平台属性列表（字段同 13.3：attrId、valueId、valueName、attrName） |
| skuSaleAttrValueList | array | 销售属性值列表（字段同 13.3：saleAttrId、saleAttrValueId、saleAttrName、saleAttrValueName） |
| skuImageList | array | 图片列表（字段同 13.3：imgName、imgUrl、spuImgId、isDefault） |

### 13.7 SKU 上架 / 下架

`GET /admin/product/onSale/{id}` ｜ 需要 Token ｜ 上架

`GET /admin/product/cancelSale/{id}` ｜ 需要 Token ｜ 下架

**请求参数**

| 位置 | 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| Path | id | number | 是 | SKU ID |

**响应 data**：`null`

> 上架后 `isSale` 变为 1，下架后变为 0。

### 13.8 删除 SKU

`DELETE /admin/product/deleteSku/{id}` ｜ 需要 Token

**请求参数**

| 位置 | 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| Path | id | number | 是 | SKU ID |

**响应 data**：`null`

---

## 附录 A：接口速查表

| # | 模块 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- | --- |
| 1 | 登录 | POST | /admin/acl/index/login | 登录获取 Token（免 Token） |
| 2 | 登录 | POST | /admin/acl/index/logout | 登出（免 Token） |
| 3 | 用户信息 | GET | /admin/acl/index/info | 获取登录用户信息 |
| 4 | 用户管理 | POST | /admin/acl/user/save | 新增用户 |
| 5 | 用户管理 | GET | /admin/acl/user/{page}/{limit} | 用户分页列表 |
| 6 | 用户管理 | PUT | /admin/acl/user/update | 更新用户 |
| 7 | 用户管理 | DELETE | /admin/acl/user/remove/{id} | 删除用户 |
| 8 | 用户管理 | DELETE | /admin/acl/user/batchRemove | 批量删除用户（Body 为 ID 数组） |
| 9 | 用户管理 | GET | /admin/acl/user/toAssign/{adminId} | 获取用户已分配角色 |
| 10 | 用户管理 | POST | /admin/acl/user/doAssignRole | 为用户分配角色 |
| 11 | 角色管理 | GET | /admin/acl/role/{page}/{limit} | 角色分页列表 |
| 12 | 角色管理 | POST | /admin/acl/role/save | 新增角色 |
| 13 | 角色管理 | PUT | /admin/acl/role/update | 更新角色 |
| 14 | 角色管理 | DELETE | /admin/acl/role/remove/{id} | 删除角色 |
| 15 | 菜单权限 | GET | /admin/acl/permission | 获取菜单树 |
| 16 | 菜单权限 | POST | /admin/acl/permission/save | 新增菜单 |
| 17 | 菜单权限 | PUT | /admin/acl/permission/update | 更新菜单 |
| 18 | 菜单权限 | DELETE | /admin/acl/permission/remove/{id} | 删除菜单 |
| 19 | 菜单权限 | GET | /admin/acl/permission/toAssign/{roleId} | 按角色回显权限树 |
| 20 | 菜单权限 | POST | /admin/acl/permission/doAssign | 给角色分配权限（Query 传参） |
| 21 | 文件上传 | POST | /admin/product/fileUpload | 上传图片（multipart） |
| 22 | 品牌管理 | GET | /admin/product/baseTrademark/{page}/{limit} | 品牌分页列表 |
| 23 | 品牌管理 | POST | /admin/product/baseTrademark/save | 新增品牌 |
| 24 | 品牌管理 | PUT | /admin/product/baseTrademark/update | 更新品牌 |
| 25 | 品牌管理 | DELETE | /admin/product/baseTrademark/remove/{id} | 删除品牌 |
| 26 | 品牌管理 | GET | /admin/product/baseTrademark/getTrademarkList | 获取所有品牌 |
| 27 | 商品分类 | GET | /admin/product/getCategory1 | 一级分类列表 |
| 28 | 商品分类 | GET | /admin/product/getCategory2/{id} | 二级分类列表 |
| 29 | 商品分类 | GET | /admin/product/getCategory3/{id} | 三级分类列表 |
| 30 | 平台属性 | GET | /admin/product/attrInfoList/{c1Id}/{c2Id}/{c3Id} | 分类下属性与属性值 |
| 31 | 平台属性 | POST | /admin/product/saveAttrInfo | 保存属性（新增/修改） |
| 32 | 平台属性 | DELETE | /admin/product/deleteAttr/{attrId} | 删除属性 |
| 33 | SPU | GET | /admin/product/{page}/{limit} | SPU 分页列表（Query 必传 category3Id） |
| 34 | SPU | POST | /admin/product/saveSpuInfo | 新增 SPU |
| 35 | SPU | POST | /admin/product/updateSpuInfo | 更新 SPU |
| 36 | SPU | DELETE | /admin/product/deleteSpu/{id} | 删除 SPU |
| 37 | SPU | GET | /admin/product/baseSaleAttrList | 全部销售属性 |
| 38 | SKU | GET | /admin/product/spuImageList/{id} | SPU 图片列表 |
| 39 | SKU | GET | /admin/product/spuSaleAttrList/{id} | SPU 销售属性列表 |
| 40 | SKU | POST | /admin/product/saveSkuInfo | 新增 SKU |
| 41 | SKU | GET | /admin/product/findBySpuId/{id} | 按 SPU 查 SKU 列表 |
| 42 | SKU | GET | /admin/product/list/{page}/{limit} | SKU 分页列表 |
| 43 | SKU | GET | /admin/product/getSkuInfo/{id} | SKU 详情 |
| 44 | SKU | GET | /admin/product/onSale/{id} | SKU 上架 |
| 45 | SKU | GET | /admin/product/cancelSale/{id} | SKU 下架 |
| 46 | SKU | DELETE | /admin/product/deleteSku/{id} | 删除 SKU |

## 附录 B：前端对接注意事项

1. 所有接口（除登录/登出）都需验证 Token，请求头字段名为 `Token`（不是 `Authorization: Bearer`）。
2. `<el-upload>` 上传时需通过 `headers` 属性携带 Token：`:headers="{ Token: userStore.token }"`。
3. 无论成功失败 HTTP 状态码均为 200，请在响应拦截器中根据 `code` 字段判断并提示 `message`。
4. 雪花 ID 为 64 位整数，超出 JS 安全整数范围（2^53-1），建议用 `json-bigint` 处理响应数据。
5. 接口返回的 `baseSaleAttrId` 等字段为 number 类型，页面使用不兼容时用 `Number()` 转换。
6. SPU 分页列表必须传 `category3Id`（Query 参数）；分页页码/条数是路径参数（如 `/1/10`）。
