# 硅谷甄选商城管理系统 · 后端

> FastAPI + SQLAlchemy 2.0 + MySQL 的商城管理系统后端 API

---

## 学习笔记目录

| Part | 主题 | 日期 | 状态 |
|------|------|------|------|
| Part 1 | 项目初始化 — 骨架搭建 | 2026-09-16 | 已完成 |
| Part 2 | 登录功能 — 公共底座、登录/登出与用户信息接口 | 2026-09-17 ~ 09-18 | 已完成 |
| Part 3 | 用户管理 — 7 个接口（分页 / 增删改 / 角色分配） | 2026-09-18 | 已完成 |
| Part 4 | 角色管理 — 4 个接口（分页 / 增改删 / 查重补丁） | 2026-09-19 | 已完成 |
| Part 5 | 权限（菜单）管理 — 6 个接口（树形结构 / 勾选回显 / Query 传参） | 2026-09-19 | 已完成 |
| Part 6 | 文件上传 + 品牌管理 — 6 个接口（multipart / 静态资源 / 品牌增删改查） | 2026-09-19 | 已完成 |
| Part 7 | 商品分类 — 3 个接口（三级级联查询 / 双 ID 引用链） | 2026-09-19 | 已完成 |
| Part 8 | 平台属性管理 — 3 个接口（嵌套结构 / 一个接口两用 / 整体覆盖） | 2026-09-19 | 已完成 |

---

## 待办清单

> 暂缓的工程化改进事项，完成后从此处移除。

- [ ] **用户模块响应 VO 化**（2026-09-18 决定，暂缓实施）— 为响应 `data` 引入 Pydantic 视图模型：新建 `app/schemas/common.py`（泛型 `PageVO[T]`）、`schemas/user.py` 追加 `UserVO`（字段驼峰直对齐契约、`extra="forbid"`）、列表接口改为 `PageVO[UserVO](...)` + `model_dump()`；统一信封 `success/fail` 不动。改造后须重跑验收回归，保证响应 JSON 逐字段等效。

---

## Part 1 · 项目初始化 — 骨架搭建

**日期：** 2026-09-16

### 目标

从零搭建一个可运行的 FastAPI 后端项目骨架，连接 MySQL 数据库，使用 SQLAlchemy 2.0 作为 ORM，预留模块扩展能力，为后续添加业务功能打好基础。

### 操作过程

#### 1. 技术选型

| 组件 | 选择 | 版本要求 | 说明 |
|------|------|----------|------|
| Web 框架 | FastAPI | >=0.115.0 | 异步、自动 Swagger 文档、类型提示友好 |
| ASGI 服务器 | Uvicorn | >=0.30.0 | 搭配 `[standard]` 安装，支持热重载 |
| ORM | SQLAlchemy | >=2.0.0 | 使用 2.0 声明式语法（`Mapped` + `mapped_column`） |
| 数据库驱动 | PyMySQL | >=1.1.0 | 纯 Python 的 MySQL 驱动 |
| 加密库 | cryptography | >=42.0.0 | PyMySQL 使用 `caching_sha2_password` 认证时所需 |
| 迁移工具 | Alembic | >=1.13.0 | SQLAlchemy 官方迁移工具 |
| 配置管理 | pydantic-settings | >=2.0.0 | 从 `.env` 文件读取配置，自带类型校验 |
| 环境变量 | python-dotenv | >=1.0.0 | pydantic-settings 的底层依赖 |

依赖写入 `requirements.txt`，通过 `pip install -r requirements.txt` 一键安装。

#### 2. 项目目录结构

```
fastAPI-guigu-shopping/
├── app/
│   ├── __init__.py
│   ├── main.py              # 应用入口 + 健康检查 + 路由注册
│   ├── config/               # 配置包
│   │   ├── __init__.py       # 导出 settings + setup_logging
│   │   ├── settings.py       # pydantic-settings 应用配置
│   │   └── logging_config.py # 日志格式与级别配置
│   ├── database.py           # SQLAlchemy 引擎 & Session 工厂
│   ├── models/
│   │   ├── __init__.py
│   │   └── base.py           # 声明式基类（id / created_at / updated_at）
│   ├── schemas/
│   │   └── __init__.py       # Pydantic 请求/响应模型（待填充）
│   ├── api/
│   │   ├── __init__.py
│   │   └── deps.py           # 公共依赖 get_db
│   └── crud/
│       └── __init__.py       # 数据库操作封装（待填充）
├── alembic/                  # 数据库迁移
│   ├── env.py                # 迁移环境配置（已对接项目 config）
│   ├── script.py.mako        # 迁移脚本模板
│   └── versions/             # 迁移版本文件
├── alembic.ini               # Alembic 配置文件
├── requirements.txt
├── .env                      # 实际配置（已 gitignore）
├── .env.example              # 模板文件（提交到 Git）
└── .gitignore
```

#### 3. 配置包（app/config/）

将应用配置和日志配置归入 `config/` 包统一管理：

**settings.py** — 使用 `pydantic-settings` 的 `BaseSettings` 从 `.env` 读取配置：

- `APP_NAME` — 应用名称，用于 Swagger 文档标题
- `DEBUG` — 调试开关，控制日志级别和 SQL 输出
- `DATABASE_URL` — MySQL 连接字符串，格式为 `mysql+pymysql://用户名:密码@主机:端口/数据库名?charset=utf8mb4`

**logging_config.py** — 统一日志配置：

- 日志格式：`时间 | 级别 | 模块名 | 内容`
- DEBUG 模式下日志级别为 DEBUG，并开启 SQLAlchemy SQL 输出
- 降低 uvicorn access 日志级别避免刷屏
- SQLAlchemy logger 设置 `propagate=False`，避免重复输出

**__init__.py** — 统一导出，外部通过 `from app.config import settings, setup_logging` 使用，无需关心内部文件结构。

#### 4. 数据库连接（database.py）

- 用 `create_engine` 创建引擎，配置了连接池（`pool_size=10`，`max_overflow=20`）和 `pool_pre_ping`（连接前检测存活）
- `SessionLocal` 是 Session 工厂，`autocommit=False`、`autoflush=False` 让事务完全手动控制
- `echo=False`：SQL 日志不由 engine 的 echo 控制，而是统一由 `config/logging_config.py` 通过 Python logging 模块管理
- `get_db()` 依赖函数不放在这里，而是统一定义在 `api/deps.py`：`database.py` 只负责基础设施（engine + Session 工厂），路由统一 `from app.api.deps import get_db` 注入 session，请求结束后自动关闭

#### 5. 模型基类（models/base.py）

使用 SQLAlchemy 2.0 的 `DeclarativeBase` 定义基类 `Base`，所有业务模型继承它后自动获得三个字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | `int`，自增主键 | 每条记录的唯一标识 |
| `created_at` | `datetime`，`server_default=func.now()` | 插入时由数据库自动生成 |
| `updated_at` | `datetime`，`onupdate=func.now()` | 每次更新时自动刷新 |

#### 6. 应用入口（main.py）

- 模块顶层调用 `setup_logging()` 初始化日志，简单直接，无需 lifespan 上下文管理器
- 健康检查 `GET /` 返回 `{"status": "ok", "app": "...", "version": "0.1.0"}`
- 预留 `include_router` 注册点，后续业务模块的路由在此挂载
- 不做自动建表，数据库结构由手动或 Alembic 迁移管理

#### 7. Alembic 数据库迁移

- 通过 `alembic init alembic` 初始化迁移目录
- 修改 `alembic/env.py`：导入项目的 `settings` 和 `Base.metadata`，用 `config.set_main_option("sqlalchemy.url", ...)` 覆盖 `alembic.ini` 中的连接字符串
- 后续添加模型后，运行 `alembic revision --autogenerate -m "描述"` 生成迁移脚本，`alembic upgrade head` 执行迁移

#### 8. 环境变量与 Git

- `.env` 存放真实配置，已加入 `.gitignore` 不提交
- `.env.example` 是模板文件，含占位符，提交到 Git 供协作者参考
- `.gitignore` 还忽略了 `__pycache__/`、`.venv/`、IDE 配置等
- 通过 `git init` 初始化仓库，首次提交包含 18 个文件（不含 `.env`）

### 原理与决策

**为什么用 pydantic-settings 而不是直接读 os.environ？**
`BaseSettings` 自动从 `.env` 文件加载环境变量，同时提供类型校验和默认值。比手动 `os.getenv()` + 类型转换更简洁安全。

**为什么用 DeclarativeBase 而不是传统的 declarative_base()？**
`declarative_base()` 是 SQLAlchemy 1.x 风格，2.0 推荐使用 `DeclarativeBase` 类继承方式，配合 `Mapped` 和 `mapped_column` 可以获得完整的类型提示支持。

**为什么用 Python logging 模块而不是 print？**
`print` 没有时间戳、级别、模块名等信息，也不方便按环境切换输出级别。`logging` 模块是 Python 标准库，支持格式统一、级别过滤、多 handler 输出，是生产项目的基本规范。

**为什么把 config.py 和 logging_config.py 合并成 config/ 包？**
随着项目发展，配置相关的文件会越来越多（如数据库配置、缓存配置等）。归入包结构后，通过 `__init__.py` 统一导出，外部引用保持简洁（`from app.config import settings`），内部结构可自由扩展。

**为什么不用 lifespan 做初始化？**
当前只有同步的日志初始化，模块顶层调用一行就够了。lifespan 适合处理需要异步初始化 + 关闭时释放的资源（如 Redis 连接池），目前没有这种需求，等后续加资源管理时再引入。

**为什么连接池设 pool_size=10、max_overflow=20？**
商城系统初期流量不大，10 个常驻连接 + 20 个临时连接足够应对。后续可根据实际负载调整。

**为什么 charset 用 utf8mb4 而不是 utf8？**
MySQL 的 `utf8` 只支持 3 字节字符，`utf8mb4` 支持 4 字节（包括 emoji 等），是真正的 UTF-8 编码。

### 踩坑记录

**1. MySQL 未连接时应用崩溃**

最初 lifespan 中直接调用 `Base.metadata.create_all(bind=engine)`，如果 MySQL 没运行，会抛出 `OperationalError` 导致应用无法启动。后来移除了自动建表逻辑，数据库结构由手动管理，应用启动不再依赖数据库可用性。

**2. cryptography 依赖缺失**

PyMySQL 连接 MySQL 8.0+ 时，默认使用 `caching_sha2_password` 认证插件，需要 `cryptography` 库来解密认证信息。如果不装会报 `RuntimeError: 'cryptography' package is required`。已在 `requirements.txt` 中加入。

**3. PowerShell 中文乱码**

在 Windows PowerShell 中通过 `urllib` 测试接口时，返回的中文内容显示为乱码。这是 PowerShell 终端编码问题（默认 GBK），不影响实际 JSON 响应内容，浏览器和 Swagger UI 中显示正常。

**4. DATABASE_URL 中密码的特殊字符**

密码 `Root@123456` 中的 `@` 在 SQLAlchemy 连接字符串中会被误解析为用户名与主机的分隔符，导致连接失败。需要将特殊字符做 URL 编码：`@` → `%40`，写成 `Root%40123456`。常见需要编码的字符还有 `:` → `%3A`、`/` → `%2F`、`#` → `%23`。

---

## Part 2 · 登录功能 — 公共底座、登录/登出与用户信息接口

**日期：** 2026-09-17 ~ 09-18

### 目标

对照 `API.md`（共 46 个接口）实现第一个完整功能模块——登录认证与用户信息（3.1 登录 / 3.2 登出 / 4.1 用户信息），并借此搭起后续所有接口都要复用的公共底座：统一响应格式、业务异常体系、JWT 签发与校验工具，以及全局鉴权依赖 `get_current_user`。

### 操作过程

#### 1. 接口盘点与开发顺序决策

盘点 `API.md` 后可以确定：46 个接口里只有 **3.1 登录** 和 **3.2 登出** 不需要 Token，其余接口全部要求请求头携带 Token。登录接口是 Token 的「生产者」——只有先能登录，才拿得到 Token 去调试其他接口，所以它必须最先写。

同时从已建好的数据库（20 张表）确认了三条关键事实：

- **双 ID 模式**：每张表都有 `id`（BIGINT 自增，物理主键，业务不用）和 `xxx_id`（业务 ID，雪花算法生成，接口层一律使用它）；关联表（如 `user_role`）里存的也是业务 ID
- **user 表数据**：`admin` 用户 `user_id=1`，密码 `111111`（明文存储，与种子数据一致）
- **Token 约定**：放在请求头 `Token` 字段（不是 `Authorization: Bearer`），有效期 1200 分钟

#### 2. 开发路线图

按依赖关系拆分：**① 模型层 → ② JWT 配置 → ③ 统一响应与异常体系 → ④ JWT 工具 → ⑤ 登录/登出接口本体 → ⑥ 鉴权依赖与用户信息接口**。前 4 步搭的是公共底座，之后每个接口都会用到；第 ⑥ 步收尾登录功能，其交付的 `get_current_user` 将成为后续所有需登录接口的统一入口。

#### 3. 步骤①：模型层（`models/`）

- **修正 `base.py`**：骨架阶段定义的列名是 `created_at` / `updated_at`，而真实表的列名是 `create_time` / `update_time`，不对齐会报 `Unknown column`；`id` 补上 `BigInteger` 类型，对齐 DDL 的 `BIGINT`
- **新增 `user.py`**：字段与 user 表逐一对应（`user_id` / `username` / `password` / `name` / `phone` / `avatar`），类型按 DDL 选 `BigInteger` / `String`
- **`__init__.py`** 统一导出 `Base` 与 `User`

#### 4. 步骤②：JWT 配置

- `settings.py` 新增三项：`JWT_SECRET_KEY`（**不写默认值 = 必填**，缺配置直接拒绝启动）、`JWT_ALGORITHM = "HS256"`、`JWT_EXPIRE_MINUTES = 1200`
- `.env` 生成 64 位十六进制随机密钥；`.env.example` 写占位符
- `requirements.txt` 增加 `pyjwt>=2.8.0`

（读取机制详见附录 A.3）

#### 5. 步骤③：统一响应 + 业务异常体系

按文档 2.2 / 2.3 落地，涉及 4 个文件：

| 文件 | 职责 |
|------|------|
| `app/exceptions.py` | `BizCode` 错误码常量（200~209）、`DEFAULT_MESSAGES` 默认提示、`BizException` 业务异常 |
| `app/utils/response.py` | `success(data)` 返回 dict；`fail(code, message)` 返回 JSONResponse（HTTP 状态码固定 200） |
| `app/api/exception_handlers.py` | 注册 4 个全局异常处理器 |
| `app/main.py` | 注册处理器；健康检查接口改用 `success()` |

4 个处理器与错误码的映射：

| 异常类型 | 处理结果 |
|----------|----------|
| `BizException` | 原样透出业务码（203 / 204 / 206 …） |
| `RequestValidationError`（参数校验失败） | 201 请求参数错误，并记 warning 日志 |
| `StarletteHTTPException`（404 等） | 统一 209；404 特判为「请求路径不存在」，其余透传 detail |
| `Exception`（兜底） | 205 服务繁忙，`logger.exception` 记录完整堆栈 |

#### 6. 步骤④：JWT 工具（`app/utils/jwt_utils.py`）

- `create_token(user_id)`：载荷只放 `user_id` + `exp`；`exp` 用 `datetime.now(timezone.utc)` 计算
- `parse_token(token)`：`jwt.decode` 自动校验签名与过期；`algorithms=[...]` 白名单；统一捕获 `jwt.PyJWTError` → 206

（概念细节详见附录 A.5）

#### 7. 步骤⑤：登录/登出接口本体

按「Schema → CRUD → 路由 → 挂载」四件套落地；路由目录按 **URL 结构镜像**组织：

```
app/routes/
└── acl/
    └── index.py    # 对应 /admin/acl/index，登录 + 登出
```

| 层 | 文件 | 内容 |
|----|------|------|
| Schema | `app/schemas/user.py` | `LoginRequest`（username / password 均为必填） |
| CRUD | `app/crud/user.py` | `get_user_by_username()`，`scalar_one_or_none()`，纯数据访问 |
| 路由 | `app/routes/acl/index.py` | `POST /login`、`POST /logout` |
| 挂载 | `app/main.py` | `app.include_router(acl_index_router)` |

登录处理流程：**收参（Pydantic 校验，缺参 → 201）→ 按用户名查库（查不到 → 203）→ 比对密码（不符 → 204）→ `create_token(user.user_id)` → `success(token)`**。

登出为无状态实现：服务端不做任何事，前端清除本地 Token 即可，直接返回 `success()`。

#### 8. 步骤⑥：鉴权依赖与用户信息接口

登录功能的收尾，交付两样东西。

**① 全局鉴权依赖 `get_current_user`**（写在 `app/api/deps.py`，与 `get_db` 同处——它将被未来几十个路由 import，且依赖方向单向、不会循环）：

```python
def get_current_user(
    token: str | None = Header(default=None, alias="Token", description="登录后获取的 Token"),
    db: Session = Depends(get_db),
) -> User:
    if not token:
        raise BizException(BizCode.NEED_LOGIN)      # 207 未携带 Token
    payload = parse_token(token)                    # 签名 / 过期校验，失败抛 206
    user = user_crud.get_user_by_user_id(db, payload["user_id"])
    if user is None:
        raise BizException(BizCode.INVALID_TOKEN)   # 206 Token 有效但用户已不存在
    return user
```

之后每个需登录的接口，参数表里声明一行 `user: User = Depends(get_current_user)` 即完成鉴权——解析 Header、校验 Token、查库、报错全部自动。（依赖链与请求级缓存机制详见附录 A.7）

**② `GET /admin/acl/index/info`**（挂在同一 router 下，prefix 自动拼出完整路径，不用改 `main.py`）。为此先补齐模型与 CRUD：

| 层 | 文件 | 内容 |
|----|------|------|
| 模型 | `app/models/role.py`、`menu.py`（新增） | `Role` / `UserRole` / `RoleMenu`、`Menu`（只映射用到的列） |
| CRUD | `app/crud/role.py`、`menu.py`（新增），`user.py`（追加） | `get_role_names_by_user_id`、`get_menus_by_user_id`（menu → role_menu → user_role 三表 join + `distinct()`）、`get_user_by_user_id` |
| 依赖 | `app/api/deps.py` | `get_current_user` |
| 路由 | `app/routes/acl/index.py` | `GET /info` |

接口数据链路：**Header Token → get_current_user 解出 user → 查角色名 + 查菜单 → 按 type 拆出 routes / buttons → 组装响应**。返回 5 个字段：

| 字段 | 来源 | 前端用途 |
|------|------|----------|
| `routes` | 菜单中 `type=1` 且 code 非空的 `code` 列表 | 过滤侧边栏菜单（与前端 `menu.ts` 的 code 对齐） |
| `buttons` | `type=2` 的 `code` 列表 | 控制按钮显隐 |
| `roles` | 用户角色名列表 | 角色展示 |
| `name` / `avatar` | user 表的 `name` / `avatar` 列 | 顶栏用户信息 |

#### 9. 验收方法

用 `TestClient` 加载真实 `app.main` 的应用实例跑断言脚本（临时脚本、跑完即删），覆盖：

- 正常路径：登录成功、Token 三段式、**反解 Token 与数据库对账**（`user_id=1`）
- 错误分支：204 / 203 / 201（缺字段、空 JSON）
- 边界：无 Token 可登录（登录免鉴权）、雪花 ID 用户（`user_id=8804574609536`）正常登录
- 元数据：OpenAPI 中两条路径与「登录认证」tag 齐全
- JWT 工具单独验收：`exp` 与真实时间误差 < 60 秒（兜住时区坑）、篡改 / 过期 / 错误密钥 / 垃圾输入 → 206
- info 与鉴权（步骤⑥）：5 个字段与数据库直连 SQL 逐项对账、多用户权限隔离（「测试」6 条 routes ≠ admin 18 条）、Token 边界全景（无 / 空 → 207；垃圾 / 篡改 / 过期 / 幽灵用户 → 206）、小写 `token` 请求头兼容

步骤⑤三轮验收（JWT 工具 10 项、登录逻辑 16 项、真实应用端到端 10 项，共 36 项断言）全部通过；步骤⑥端到端验收 32 项亦全部通过。期间共发现 4 处问题，均已修复（见踩坑记录）。

### 原理与决策

**为什么先写登录接口？**
它是唯一免 Token 的入口，是 Token 的「生产者」；写它的过程会倒逼出模型、配置、统一响应、异常体系、鉴权工具等全部公共底座，是成本最低的首个接口。

**为什么响应 HTTP 状态码永远 200、业务状态放 `code`？**
业务错误（密码错误、用户不存在）不是 HTTP 语义错误，HTTP 200 只代表「请求已成功送达并处理」；前端在统一的响应拦截器里读 `code` 分流，一处处理全部错误形态，同时避免代理、网关等网络层对 4xx/5xx 的额外干预。这是与 Java 版课程后端 `Result` 结构对齐的约定。

**为什么 Token 载荷只放 `user_id`？**
JWT 载荷只是 Base64 编码而非加密，任何人都能解开，所以不放敏感信息；只放业务标识，其余信息每次请求由后端按 `user_id` 查库取最新值，也避免「载荷数据过期不一致」。

**为什么 `exp` 必须用带时区的 UTC 时间？**
JWT 规范中 `exp` 是 UTC 时间戳；naive 本地时间（UTC+8）会被按 UTC 解释，Token 有效期凭空多出 8 小时。详见附录 A.5。

**为什么 `jwt.decode` 必须传 `algorithms` 白名单？**
防算法混淆攻击（攻击者篡改 header 中的算法声明骗过校验），PyJWT 也强制要求显式指定，是安全基线。

**为什么 203（用户名不存在）与 204（密码错误）要分开？**
按文档要求区分。真实系统出于安全考虑常统一提示「用户名或密码错误」，避免攻击者探测哪些用户名存在；本项目以文档为准。

**为什么异常处理器必须返回 Response？**
这是 Starlette 的异常处理契约：处理器要产出最终的 Response 对象，所以 `fail()` 返回 `JSONResponse`；而正常路由里 `success()` 返回普通 dict 即可，由 FastAPI 负责序列化。两条路径各司其职。

**为什么路由层薄、CRUD 纯、工具层独立？**
路由只做编排（查库 → 判断 → 签发 → 返回），不写 SQL；CRUD 只做数据访问，不做业务判断；JWT 工具只管签发解析。三层各管一段，后续接口全部沿用这个分工。

**为什么把鉴权做成 `get_current_user` 依赖，而不是每个接口手写解析？**
声明式接入：接口签名里写一行 `Depends(get_current_user)`，解析 Header、校验 Token、查库、报错全部自动；FastAPI 递归装配整条依赖链，且同一请求内依赖带缓存——端点和依赖里写的 `Depends(get_db)` 是同一个 session。鉴权失败统一抛 207 / 206 交给全局异常处理器，一处编写、后续 40+ 个接口复用。

**为什么没带 Token 是 207、Token 无效却抛 206？**
语义分流：207 = 「未登录」——前端应跳登录页；206 = 「凭证无效」（伪造、篡改、过期、用户已不存在）——前端应清除本地 Token 提示重新登录。分开报码，前端拦截器才能分别处理。

**为什么查角色 / 菜单用显式 join，不配 `relationship()`？**
本库表间按**业务 ID** 关联而非物理外键，配 `relationship()` 需要显式指定 `primaryjoin` 等参数，且默认懒加载会把 SQL 藏在属性访问背后；显式 join 每条 SQL 一目了然。另外三表 join 必须 `.distinct()`——用户身兼多角色、角色间菜单重叠时，join 会把同一行放大成多条。

**为什么 routes 要过滤空 code、又必须包含每一级菜单的 code？**
menu 表里有「全部数据」这类 code 为空字符串的节点，它们不是权限，塞进 routes 会污染列表；同时前端「整枝过滤」要求父菜单的 code（如 `Acl`、`Product`）也在列表里，否则子菜单会被连带误杀。两个细节合起来才是完整的前端权限契约。

**为什么 `name` 返回「管理员」而不是「admin」？**
`name` 对应 user 表的 `name` 列（昵称），前端顶栏就是拿它做展示。`API.md` 的示例值仅为示意——其 roles 示例写「系统管理员」，而库里真实值是「超级管理员」——**取值以数据库为准，文档示例不可尽信**。

### 踩坑记录

**1. `BigInteger` 未导入 → NameError**

`base.py` 中给 `id` 用了 `BigInteger`，但导入行只写了 `from sqlalchemy import DateTime, func`，启动即 `NameError: name 'BigInteger' is not defined`。**教训**：新增 SQLAlchemy 类型时同步补 import。

**2. `env()` 不存在 → NameError**

受 Django 经验影响写出 `JWT_SECRET_KEY: str = env("JWT_SECRET_KEY")`，而 `env()` 是 django-environ 的 API，pydantic-settings 中不存在，import 阶段直接崩。正确表达是**不写默认值**：不写即必填，读取交给 `Settings()` 实例化那一刻（详见附录 A.3）。

**3. `main.py` 重复导入**

同一行 import 写了两遍（无害但冗余），已删除。

**4. import 路径与文件夹层级对不上 → ModuleNotFoundError**

路由文件实际建在 `app/routes/`，但 `main.py` 里按 `app.api.routes.acl.index` 导入，启动报 `ModuleNotFoundError: No module named 'app.api.routes'`。**Python 的 import 路径必须与文件夹层级逐层对应**；文件位置调整后 import 必须同步改。

> 连带教训：编辑器里改完必须保存到磁盘。验收时真实发生过：IDE 里已经改好、磁盘上还没保存，Python 读到的一直是旧内容——「我明明改了」和「程序读到的」是两回事。

**5. naive 时间当 UTC 用（时区坑）**

`exp` 若用 `datetime.now()`（本地时间 UTC+8）会被按 UTC 解释，Token 有效期白送 8 小时；必须 `datetime.now(timezone.utc)`。详见附录 A.5。

---

## Part 3 · 用户管理 — 7 个接口

**日期：** 2026-09-18

### 目标

实现 `API.md` 第 5 章「用户管理」全部 7 个接口——5.1 新增 / 5.2 分页列表 / 5.3 更新 / 5.4 删除 / 5.5 批量删除 / 5.6 查已分配角色 / 5.7 分配角色。全部需登录（`get_current_user`），沿用 Part 2 的三层分工（Schema → CRUD → 路由）与统一响应体系，并首次引入雪花算法生成业务 ID。

### 操作过程

#### 1. 路线图：四步闭环，每步验收

| 步骤 | 接口 | 验收结果 |
|------|------|----------|
| ① 分页列表 | 5.2 | 44 项断言全过 |
| ② 雪花 ID + 新增 + 更新 | 5.1 / 5.3 | 45 项全过 |
| ③ 删除 + 批量删除 | 5.4 / 5.5 | 37 项全过 |
| ④ 查已分配角色 + 分配角色 | 5.6 / 5.7 | 36 项全过 |

先写 5.2 列表：后续接口的验收都依赖「能查出数据」这个观察窗口。

#### 2. 分页列表（5.2）

- `GET /admin/acl/user/{page}/{limit}`，`username` 查询参数可选，`LIKE %..%` 模糊搜索
- `page` / `limit` **用 `str` 接收**再手动容错（非法值兜底 1 / 10）——契约定 2.4 要求非法值兜底而不是报错（连锁影响见下「路由顺序」与附录 A.8）
- **避免 N+1**：不逐行查角色，改为一次 `IN` 查询批量取角色名 map，整页数据固定 2 条 SQL
- 响应五件套：`records / total / size / current / pages`（pages 用 `(total + limit - 1) // limit` 向上取整）

#### 3. 雪花 ID + 新增 + 更新（5.1 / 5.3）

- 业务 ID `user_id` 由应用层雪花算法生成（见附录 A.2），接口层只暴露业务 ID
- 新增：用户名查重（已存在 → 202）→ 入库；并发竞态交给 DB 唯一索引兜底（`IntegrityError` 被全局处理器接住 → 205）
- 更新：先查目标、存在才改；**不存在时幂等静默成功**（契约未定义「用户不存在」错误码）
- 请求体字段用 `Field(min_length=1, max_length=64)` 对齐 DDL 长度

#### 4. 删除 + 批量删除（5.4 / 5.5）

单个删除复用批量删除，核心在 CRUD 层一个函数：

```python
def delete_users(db: Session, user_ids: list[int]) -> None:
    """批量删除用户（含单个删除）；同时清理 user_role 中的角色关联；不存在的 ID 静默忽略（幂等）"""
    if not user_ids:
        return
    db.execute(delete(UserRole).where(UserRole.user_id.in_(user_ids)))   # 先清子表关联
    db.execute(delete(User).where(User.user_id.in_(user_ids)))           # 再删主表
    db.commit()
```

- 级联清理 `user_role`：同一事务「先子后父」，一次 commit
- 批量接口请求体是**裸 JSON 数组**（`[123, 456]`）：必须显式 `Body(...)` 声明，否则会被当作查询参数；`min_length=1` 把空数组拦为 201

#### 5. 查已分配角色 + 分配角色（5.6 / 5.7）

- `GET /toAssign/{adminId}` 一次返回两个列表：`assignRoles`（该用户已有）+ `allRolesList`（系统全部）——前端穿梭框的两侧数据
- Role 统一归一化为契约结构：`id / roleName / remark（NULL → ""）/ createTime（yyyy-MM-dd HH:mm:ss）`
- `POST /doAssignRole` 是**全量覆盖**语义：提交列表即最终结果，空列表 = 清空：

```python
def replace_user_roles(db: Session, user_id: int, role_ids: list[int]) -> None:
    """全量覆盖用户角色：先清空旧关联，再插入新关联（空列表=清空）"""
    db.execute(delete(UserRole).where(UserRole.user_id == user_id))
    if role_ids:
        db.add_all([UserRole(user_id=user_id, role_id=rid) for rid in role_ids])
    db.commit()
```

- 契约沉默点坚持不发明逻辑：不校验 `role_id` 是否存在、`userId` 不存在也不报错（如实按契约实现）

#### 6. 路由顺序：本章最大的雷

`app/routes/acl/user.py` 的注册顺序必须为：

```
save → update → remove/{id} → batchRemove → toAssign/{adminId} → doAssignRole → {page}/{limit}（通配最后）
```

`GET /toAssign/{adminId}` 与通配 `GET /{page}/{limit}` 是**同一形状**（两段路径 + GET）——顺序写反，`/toAssign/1` 会被通配接走、返回用户分页列表（前端静默拿错数据）。匹配机制详见附录 A.8。

#### 7. 验收方法与结果

TestClient 直跑 `app.main`、临时脚本断言、造数走接口 + 直连 DB 对账、跑完即删。四步合计 **162 项断言全部通过**；每步结束复验数据库零污染（user / user_role / role 表与 admin 角色对账全部回基线）。期间发现 3 处代码问题（见踩坑记录），修复后全部复验通过。

### 原理与决策

**为什么列表接口先写？**
它是「观察窗口」——新增/删除的验收都要靠列表接口查数据来对账；先有读、再有写。

**为什么 `page` / `limit` 用 `str` 接收再手动解析？**
若声明成 `int`，请求 `/abc/10` 会在参数解析阶段被拦下 → 201；而契约 2.4 要求「非法值按默认值兜底」。用 `str` 收下、手动判断转换，才能把兜底权握在手里。这也直接决定了通配路由是「宽松匹配」——宽松意味着贪吃，贪吃就必须排最后（A.8）。

**为什么删除/更新「目标不存在」按幂等静默处理？**
契约错误码表没有定义这两种场景。幂等语义下，删除的目标是「不存在」、更新的目标是「已是期望值」——**达到期望状态的失败无需报错**。不发明契约之外的行为。

**为什么批量删除必须显式 `Body(...)`？**
FastAPI 中 `list[int]` 默认按**查询参数**解析（期望 `?ids=1&ids=2`）；裸 JSON 数组体必须显式 `Body(...)` 才会被当作请求体。空数组则由 `min_length=1` 拦截 → 201（契约括注「不能为空」）。

**为什么角色分配设计成「全量覆盖」？**
契约定义如此，且匹配前端交互——穿梭框/复选框提交的永远是「最终全集」，不是增量。实现上「先删后插」一次事务：天然幂等、天然支持清空（空列表）、不用做差集计算。

**为什么删用户要级联清理 `user_role`？**
否则留下「幽灵关联」：关联表里残留已删用户的记录，以后按角色统计用户数、或按用户查角色时都会出错。同一事务先子后父，保证「要么都成功、要么都回滚」。

**为什么接口层只暴露业务 ID（`user_id`），不用自增主键 `id`？**
延续 Part 2「双 ID 模式」：物理主键 `id` 只服务于 DB（自增、索引紧凑），业务 ID（雪花）对外——不泄露业务规模、跨系统可合并（见附录 A.2）。

**为什么这一章不引入 Pydantic 响应模型（VO）？**
讨论后决定暂缓：当前裸 dict 组装先保证契约正确，响应 VO 化（`PageVO[T]` + `UserVO` 等）属于工程化增强，已记入待办清单，完成后再做字段级等效回归。

### 踩坑记录

**1. CRUD 函数误写进路由文件（层归属错误）**

`delete_users` 被写成了路由文件里的一个无装饰器裸函数，路由再调用 `user_crud.delete_users` → `AttributeError` → 205。**教训**：路由层只做编排（收参 → 调 CRUD → 套信封），一切 SQL 与事务归 CRUD 层；新增函数前先问「它属于哪一层」。

**2. 路由通配「贪吃」：`GET /remove/123` 之谜**

删除接口是 `DELETE /remove/{id}`，用 `GET /remove/123` 试探时预期 405/209——实际却拿到用户分页数据 200（SQL 铁证：`SELECT ... LIMIT 0, 999999999999999`）。原因：Starlette **先翻完全部路由找 FULL（路径+方法都匹配）**，找不到才用 PARTIAL（路径匹配、方法不符）报 405——而 `GET /{page}/{limit}` 正好是 FULL，把请求兜走了。只有 `POST /remove/123`（GET 通配吃不下、又无其他 FULL）才会走 405 → 209。机制细节见附录 A.8。

**3. 复制粘贴事故：三处新代码各写了两份**

新增的 3 个 CRUD 函数、1 个 Schema 类、2 条路由在整个文件里各出现两次。功能上侥幸没事（Python 同名后定义覆盖前定义），但 `@router` 装饰器**在模块导入时立即注册**——实际注册了重复路由，启动日志出现 `Duplicate Operation ID ...` warning ×2。真正的危险：以后只改「其中一份」时出现「改了没生效」的灵异 bug。已逐段删净并复验（36 项断言 + warning 消失）。**教训**：装饰器语法下，「函数重复定义」不是无害冗余，是真实的路由注册。

**4. 验收脚本两次断言预期写错（HTTP 状态码 vs 业务码）**

① `GET /remove/123` 预期 209、实际被通配 FULL 接走（见坑 2）；② 错误码断言写成 `r.status_code == 201/207`，而全项目的 HTTP 状态码恒为 200、错误码在响应体 `code` 字段——**断言错误码必须读 `body.code`**。两次都是「验收入口」的预期错了、不是被测代码错了。**教训**：验收脚本本身也是代码，失败时先核实「预期」对不对，再怀疑「实现」。

---

## Part 4 · 角色管理 — 4 个接口

**日期：** 2026-09-19

### 目标

实现 `API.md` 第 6 章全部 4 个接口——6.1 分页列表 / 6.2 新增 / 6.3 更新 / 6.4 删除。接口模式全部来自第 5 章的练手（分页五件套、雪花 ID、幂等更新、关联清理），本章真正的主题是**代码复用**：当第 5 章的私有函数被第二个模块需要时，如何做一次干净的小重构；以及在「契约沉默 + 数据库事实」冲突时如何修正决策。

### 操作过程

#### 1. 路线图

| 步骤 | 内容 | 验收结果 |
|------|------|----------|
| ① | 6.1 分页列表 + 共享函数重构 | 28 项断言全过 |
| ② | 6.2 / 6.3 / 6.4 增改删 | 一期验收 43 项全过 |
| 补丁 | 6.2 显式查重（B 方案） | 14 项全过 |

#### 2. 重构：第二次复用就提取

第 5 章写在 `routes/acl/user.py` 里的两个私有函数，被角色模块第二次需要，按「提取 / 不提取」分别处置：

| 函数 | 去向 | 理由 |
|------|------|------|
| `_fmt_role` | 提取为 `schemas/role.py` 的 `role_to_dict` | 两个调用方要的契约结构一字不差 |
| `_parse_path_int` | 提取为 `utils/parse.py` 的 `parse_path_int` | 纯数值容错、与实体无关；第 7 章菜单分页还会用 |
| `_fmt_time` | 保留两份（user.py / schemas/role.py 各一） | 只有各自上下文的需求，等第三处出现再上移 |

`user.py` 侧重构收尾：删掉两个旧函数、清理失效的 `from app.models.role import Role`、两处调用点换名——重构的完成定义是「旧引用一个不剩」，回归验收 7 项断言确认第 5 章接口零损伤。

#### 3. 分页列表（6.1）

与 `get_user_page` 逐行对照，只有三处不同（表名、排序字段、搜索字段）。角色列表不需要「归属」信息，省去第 5 章的批量查角色名一步，整个路由比用户分页短一截。

#### 4. 增改删（6.2 / 6.3 / 6.4）

- **新增**：雪花 ID 入库；update 场景幂等静默（契约未定义「角色不存在」）
- **更新**：`remark` 全量覆盖语义——不传即清空为 NULL，与 `update_user` 同哲学
- **删除**：`delete_role` 连带清理 `user_role` + `role_menu` **两张**关联表（角色两头挂关系）；先关联后本体、同一事务一次 commit
- **YAGNI**：角色模块没有 batchRemove 契约，crud 删除函数写单 ID 版，不预先泛化

#### 5. 一期验收的意外收获：讲授假设被数据库推翻

43 项验收脚本第一轮跑到「同名角色创建」时被 `IntegrityError` 中断——`role` 表存在 `role_name` 唯一索引 `idx_role_name`（讲授时假设没有）。同名 save 实际被全局兜底接住，返回 **205「服务繁忙」**：把用户输错名字伪装成了服务器故障。

决策拍板（B 方案）：`save_role` 补显式查重，命中抛 `BizException(201, "角色名已存在")`；唯一索引继续兜并发竞态（毫秒级双双通过查重时撞索引走 205）。补丁后 14 项专项断言全过，update 维持现状不查重（粒度对齐第 5 章）。

#### 6. 验收方法

三段 TestClient 脚本共 **85 项断言**全部通过：步骤① 28 项（6.1 全链路 + 重构回归）、一期 43 项（增改删全链路 + 删除级联白盒验证：预插 `user_role` / `role_menu` 关联行 → 删角色 → 三表全清 + 第 5 章集成回归）、补丁 14 项。每段结束复验测试数据零残留；期间发现 1 处讲授假设错误（见踩坑记录），修正后复验通过。

### 原理与决策

**为什么第二次复用就提取，不等第三次（Rule of Three 的正确用法）？**
经典说法是「第三次才抽象」，针对的是相似但不相同的代码——需要归纳恰当的抽象面。这里两处需求**逐字符相同**，不存在抽象设计成本，第二次就提取。判据是「调用方要的东西是否一字不差」而不是机械数次数；同理 `_fmt_time` 暂留两份，因为提取时机本身也是成本。

**为什么 `role_to_dict` 归 schemas、`parse_path_int` 归 utils？**
按职责归类：schemas 层管「数据形状」——请求体长什么样、实体怎么变契约结构；`parse_path_int` 与任何实体无关，是纯数值容错，归 utils。依赖单向（schemas → models），无循环导入。

**为什么删除角色要清两张关联表？**
角色是权限体系的中间实体：`user_role` 连用户、`role_menu` 连菜单。只删本体则两张表残留指向不存在角色的孤儿行，以后按角色统计、按用户查权限都会出错。与第 5 章删用户清 `user_role` 完全对称，只是角色两头挂关系。

**为什么 save 查重、update 不查重？**
新增是「创建身份」，撞名概率高、明确报错价值大；更新场景前端回显原名，撞名概率低，YAGNI——真撞了有唯一索引兜底（实测 205 且事务回滚、数据不脏）。与第 5 章 save_user / update_user 的粒度完全对齐。

**为什么同名错误用 201 + 自定义 message，不发明新码？**
202 在契约中是「用户名已存在」的专属码，角色查重契约未定义任何专属码。`BizException(code, message)` 的 message 参数可覆盖默认提示——用通用参数错误码 + 明确提示语，照契约办事、不发明语义。

**为什么「显式查重 + 唯一索引」要双层？**
显式查重管体验（99.9% 场景返回明确错误）、索引管竞态（并发双双通过查重时落库拦截）。索引不能包办一切：`IntegrityError` 只能被兜底成「服务繁忙」，用户完全无法理解——这正是补 B 方案的原因。

### 踩坑记录

**1. 讲授假设被数据库事实推翻（role_name 唯一索引）**
「新增不查重」的决策依据是契约未定义查重错误码 + 假设无唯一索引，第二个前提错了。**教训**：契约沉默时还要核数据库事实——表结构（索引、约束）是契约之外的第二个事实来源；验收脚本用断言固化预期，假设错了脚本当场中断，这正是验收的价值，失败比全绿更有信息量。

**2. TestClient 默认把服务端异常抛进测试进程**
第一轮脚本中断时 `IntegrityError` 堆栈直接打进脚本输出——TestClient 默认 `raise_server_exceptions=True`，模拟的是「进程内调用」而非真实 HTTP。加 `raise_server_exceptions=False` 后，服务端异常才走全局异常处理器、返回 205 JSON 响应，与线上行为一致。**教训**：TestClient 测异常路径必须关掉这个默认值。

**3. 中断脚本的残留数据**
第一轮脚本中断在清理段之前，库里残留测试角色。给脚本加「预清理」段（按测试前缀删旧数据）保证可重跑。**教训**：验收脚本要按可重复执行设计，任何一次中断都不能污染下一轮。

---

## Part 5 · 权限（菜单）管理 — 6 个接口

**日期：** 2026-09-19

### 目标

实现 `API.md` 第 7 章全部 6 个接口——7.1 菜单树 / 7.2 新增 / 7.3 更新 / 7.4 删除（首次启用 208）/ 7.5 回显权限树 / 7.6 分配权限（Query 传参）。本章的核心新知识是**平铺表 → 树形结构**的组树算法；同时把 Part 4 的教训「契约沉默时核数据库事实」前置或为开工仪式。

### 操作过程

#### 1. 事实核对先行（Part 4 教训的兑现）

写代码前先跑勘察脚本直连数据库，把所有影响设计的存量事实摸清：

| 数据库事实 | 对设计的影响 |
|------|------|
| 63 条菜单，单根「全部数据」（menu_id=1，pid=0），其余全挂它下 | 树的预期形状；pid=0 新建会造出第二棵根 |
| `status` / `to_code` 列 NOT NULL 且无默认值 | 模型补映射 status；create 必须显式置 `""` |
| 表里有个 `select` 列（63 条全 0） | 摆设列——不映射，输出按 7.1/7.5 语义计算 |
| `name` 无唯一索引 | 查重无索引兑底；查重函数不能用 `scalar_one_or_none()` |
| type 实测有 0/1/2 三值；还有 type=2 且 level=2 的种子行 | 契约括注「按钮须配 level=4」数据上不成立——放弃跨字段硬校验 |
| `role_menu` 角色一有 126 行（> 63，含重复） | 读侧 set 去重；写侧输入保序去重 |
| `@router.get("")` 配 prefix 实测 200 可用 | 7.1 的空路径路由写法 |

#### 2. 组树：平铺表 → 嵌套结构（本章灵魂）

menu 表是**邻接表模型**存树：每行 `pid` 指向父节点 `menu_id`，根 pid=0。契约要嵌套 children，需要一次变换：

- **反模式（N+1）**：递归查库，每个父节点一次 SELECT，63 条菜单 63+ 次查库
- **正模式（O(n)）**：一条 `SELECT * ORDER BY menu_id` 查全表 → 全部实体转 dict 并以 menu_id 建字典索引（O(1) 找爹）→ 单循环挂树：pid 在字典里找到爹就 append 进爹的 children，找不到（pid=0 或孤儿）就是根

顺序稳定性免费获得：列表按 menu_id 升序，append 天然有序。两个防御性细节：孤儿节点按根处理（可见可删，优于静默消失）；`parent is not node` 防自环脏数据。适用边界：全表加载成立于「小表 + 低频后台」，百万级要换递归 CTE 或闭包表。

#### 3. 六接口落地要点

- **7.1**：`@router.get("")`；select 恒 False（勾选回显是 7.5 的事）
- **7.2**：名称查重（契约括注「不能与已有菜单重复」→ 201）；无索引兑底，竞态窗口如实接受
- **7.3**：只改契约定义的 name/pid/code/level 四字段，type 一个都不动
- **7.4**：`BizCode.MENU_HAS_CHILDREN`（208）定义于 Part 2、今日首次启用；删除级联清 `role_menu`
- **7.5**：查一次 role_menu 得 `set[menu_id]`（set 去重 + O(1) in），组树时标注 select=True，结构逻辑完全复用
- **7.6**：roleId / permissionId 走 **URL Query**（简单类型参数零装饰器即默认 Query，与 5.7 裸数组必须显式 `Body(...)` 互为镜像）；逗号切分 + 过滤空段 + `dict.fromkeys` 保序去重；空串 = 清空

#### 4. 自主重构：路由聚合注册

落地时顺手把 `main.py` 的逐条 import 改为聚合模式：`routes/acl/__init__.py` 里建空 `APIRouter()` 依次 `include_router` 四个子 router，`main.py` 只剩一行注册。新增模块时 main.py 不再变动。各文件内部的路由顺序纪律（具体在前、通配在后）不受聚合影响——那是文件内装饰器顺序决定的。

#### 5. 验收方法与结果

TestClient 直跑真实应用，54 项断言全过：

- **组树结构**（11 项）：单根、递归清点 63 节点、字段恰 10 键、叶子 children=[]、兄弟按 menu_id 升序、样例节点逐字段对账（id=7 / id=11）
- **7.5 回显白盒**（4 项）：select=True 集合与 DB `SELECT DISTINCT menu_id FROM role_menu WHERE role_id=1` 完全对账（126 行含重复 → set 去重后 63）；不存在角色 → 静默全 False
- **7.2/7.3/7.4 全链路**（22 项）：查重 201、越界 201、入库 to_code/status 空串对齐、type 不被 update 触碰、208 提示语、role_menu 级联清理、幂等
- **7.6 Query 怪参**（8 项）：分配对账、重复 ID 去重、含字母 201、空串清空
- **回归 + 清理**（9 项）：/info（menu 模型加列后）、用户/角色分页、toAssign（聚合注册下无路由冲突）、零残留、树回 63 节点

### 原理与决策

**为什么关系型库用邻接表存树？**
平铺行才能用 SQL 灵活查询、加约束、局部更新；嵌套 JSON 是展示形状，不是存储形状。存与展分离，变换在应用层做。

**为什么字典索引 + 单循环挂树是 O(n)？**
全部节点先进 dict（menu_id → 节点），之后每个节点找爹是一次 O(1) 字典命中——反观递归查库，每次找爹都是一次数据库往返。算法复杂度的差别本质是「找爹的成本」的差别。

**为什么不映射表里的 select 列？**
63 条全 0，勾选的事实来源是 role_menu 关联表。映射一个摆设列只会误导后续维护者以为「改列就能改勾选」。输出的 select 是按 7.1（恒 False）/ 7.5（对账 role_menu）语义计算的。

**为什么查重函数用 `limit(1).first()` 而不是 `scalar_one_or_none()`？**
`scalar_one_or_none()` 命中多条会抛 `MultipleResultsFound`——它隐含「至多一条」的契约，这个契约由唯一索引保证。menu.name 没有唯一索引，同名多条是合法数据形态，必须 limit(1)+first()。与 Part 4 的 `get_role_by_role_name` 对照：同一个需求，索引事实决定函数写法。

**为什么 doAssign 的参数零装饰器？**
FastAPI 中简单类型（int/str/float/bool）参数默认即 Query——契约选 Query 传参时零成本对齐。这是 5.7 裸数组必须显式 `Body(...)` 的镜像知识：裸数组默认会被当查询参数，简单标量默认就是查询参数。

**为什么 parse 阶段要 `dict.fromkeys` 去重？**
role_menu 存量有重复行，前端勾选树可能因脏数据回传重复 ID；不去重则 replace 后又写入重复行，脏数据永久自复制。保序去重还保证写入顺序稳定。

### 踩坑记录

**1. 验收脚本断言预期又错一次（pid=0 语义）**
创建测试菜单传 pid=0，断言它挂在「全部数据」的 children 末尾——实际它成为**独立的第二个根**（组树规则：pid=0 视为根；存量形态里「全部数据」之下才是业务菜单，pid=0 只有它自己）。总数 65 的断言同时通过，恰好证明树组得完全正确，错的只是预期。与 Part 3 坑 4 同型：**验收脚本也是代码，FAIL 先怀疑预期再怀疑实现**。连带发现一个契约语义与存量数据的微妙分叉：契约说「一级菜单传 0」，但存量的「一级」其实挂在根节点之下——pid=0 会造出多棵根树，前端树控件吃根数组一般无碍，但值得知道。

**2. 契约括注与数据事实冲突（type=2 且 level=2）**
契约 7.2 括注「按钮节点须配 level=4」，但库里有 type=2 却 level=2 的种子行、还有 4 条 type=0。若做跨字段硬校验（type=2 必须配 level=4），这些存量节点连「原样更新」都过不了校验。决策：只做字段级范围校验（type ∈ [1,2]、level ∈ [1,4]），不发明跨字段约束——契约括注描述的是理想数据，不是存量事实。

---

## Part 6 · 文件上传 + 品牌管理 — 6 个接口

**日期：** 2026-09-19

### 目标

实现 `API.md` 第 8 章（文件上传）与第 9 章（品牌管理）共 6 个接口。两章合为一个 Part：8.1 上传产出的 URL 正是 9.2 新增品牌的 `logoUrl` 来源，一条业务链。本 Part 引入三样全新基础设施：multipart 文件上传、静态资源服务、以及第一个非 ACL 模块（`/admin/product` 域，新开 `routes/product/` 包）。

### 操作过程

#### 1. 事实核对先行（延续 Part 5 的开工仪式）

| 事实 | 影响 |
|------|------|
| 表名 `trademark`；双 ID（id + tm_id，idx_tm_id 唯一） | 双 ID 模式第四张表，雪花照旧 |
| **tm_name 有唯一索引 idx_tm_name** | save 查重 = 第 6 章 B 方案同构（显式 201 + 索引兑竞态 205），这次先核过事实 |
| 存量 logoUrl 全是 `/api/static/img/sph/{日期}/{文件名}` | 返回 URL 的契约形状实锤 |
| python-multipart 已装（0.0.6）但 requirements.txt 未声明 | 补声明——隐式依赖是环境复现的坑 |
| 项目无 static/ 目录，.gitignore 无相关条目 | 启动自举 mkdir + gitignore 补 `/static/` |
| spu 表有 tm_id 引用；category3 没有 | 删除品牌决策依据 |

#### 2. 8.1 文件上传

- `UploadFile = File(...)` 接 multipart 表单；`UploadFile.file` 是 SpooledTemporaryFile（<1MB 进内存，超出溢写磁盘）
- 校验：content_type 不以 `image/` 开头 → 201「只能上传图片文件」；缺 file 字段 → Pydantic 拦截 → 全局处理器 → 201（老路子自动接住）
- 存储：按日期归档 `static/img/sph/{yyyymmdd}/`；文件名 = `{雪花ID}-{basename}`；`shutil.copyfileobj` 流式落盘
- 返回契约形状 URL：`/api/static/img/sph/{日期}/{雪花-原名}`

#### 3. `/api` 前缀之谜

后端没有 `/api` 前缀，但契约响应和 DB 存量 logoUrl 都是 `/api/static/...`。推理闭环：前端所有请求以 `/api` 开头走代理，而我们的 ACL 路由是 `/admin/acl/...`（无 /api）且前端正常工作——**说明代理必然剥掉 `/api` 再转发**。所以：mount 在 `/static`（代理剥完后真正到达的路径），返回 `/api/static/...`（契约 + 存量形状）。浏览器拿 URL 带着走代理→剥 /api→打到 /static→取到图。

#### 4. 静态资源服务

`app.mount("/static", StaticFiles(directory="static"), name="static")`——mount 是**子应用挂载**不是路由注册：请求路径以 /static 开头的整段截走交给 StaticFiles 处理，不进路由表、与 API 路由零冲突。坑：directory 不存在会直接 RuntimeError，所以 mount 前先 `Path("static").mkdir(exist_ok=True)` 自举。

#### 5. 品牌五接口（全旧模式）

- 9.1 分页：无搜索参数（比 user/role 还简），parse_path_int 容错照旧
- 9.2 查重：同构 role 的 B 方案（`scalar_one_or_none`，唯一索引撑腰）；同 201「品牌名已存在」+ 索引兑竞态 205
- 9.3 幂等更新两字段；9.4 无级联（tm 是叶子实体，spu.tm_id 是业务引用，契约未定义拦截，Java 版同样不管）
- 9.5 不分页全量，元素与 9.1 records 同构（契约主句「同 9.1 的 records」+ 括注列 3 字段，按主句取 4 字段含 createTime）
- **路由顺序本章唯一真实的雷**：`GET /getTrademarkList` 与通配 `GET /{page}/{limit}` 同形状（两段 + GET），必须注册在通配前，否则被当成 `page="getTrademarkList"` 兜底成空分页

#### 6. routes/product 新包

新 URL 域开新包，沿用聚合注册：`routes/product/__init__.py` 聚合 file_upload + trademark 两个子 router，main.py 一行注册。

#### 7. 验收方法与结果

57 项断言全过：

- **8.1 上传（21 项）**：鉴权 207/206、非图片/缺字段/空文件名 201、**落盘字节与上传内容一致**、GET /static 取回字节一致 + Content-Type、**同名二次上传两个不同 URL 两文件都在（防覆盖）**、**路径穿越 `../../evil.png` 只落 basename 且不出现在上级目录**
- **9.x 品牌（29 项）**：鉴权、分页五件套 + 容错、查重 201+提示语、增改删全链路 DB 对账、**9.5 活着且是数组（路由顺序正面断言）**
- **回归 + 清理（7 项）**：健康检查、/info、用户/角色分页、菜单树 63、品牌与上传文件零残留

### 原理与决策

**为什么 8+9 合一个 Part？**
8.1 的输出是 9.2 的输入，分开讲会割裂业务链；且两章体量都不足以独立成 Part。

**为什么 mount /static 却返回 /api/static？**
存的是服务内真实路径（代理剥完 /api 后到达的），返回的是契约/存量形状（前端拼 VITE_APP_BASE_API 直接可用）。两端各说各的实话，代理负责翻译。

**为什么文件名加雪花前缀 + basename？**
前缀防同日同名覆盖（否则后传静默覆盖先传，数据丢失级 bug；URL 只需是 string，文件名不是契约点）；basename 防路径穿越——恶意 filename 可以是 `../../app/main.py`，不清洗就可能写到任意路径，文件上传的经典安全必修课。

**为什么 copyfileobj 流式拷贝？**
`file.file.read()` 整读会把整个文件拉进内存；copyfileobj 分块搬，大文件不必全内存。

**为什么上传路由不声明 db 依赖？**
它不碰数据库。`get_current_user` 内部自己拿 db，路由没必要陪绑用不上的参数——依赖按需声明。

**为什么 requirements 必须声明 python-multipart？**
能跑是当前环境恰好装了（被谁装的都不知道）。隐式依赖 = 换环境就崩 + 谁也说不清为什么需要它。能跑 ≠ 已声明。

### 踩坑记录

**1. 讲义「错误示例 + 修正版」引发的 import 缺失**
讲授 crud 的 delete 函数时先展示了 `__table__.delete()` 错误写法又给修正版（标准 `delete(Trademark)` + 配套 import）。合并时函数体取了修正版、import 行漏了 `delete` → 调用即 NameError → 205。静态验收抓住（运行前拦住，未浪费一轮跑测）。**教训**：错误示例有价值，但配套改动必须以清单形式列死；「正确函数体 + 旧 import」是复制合并的高发事故形态。

**2. docstring 抄串（ACL → product）**
从 `routes/acl/__init__.py` 复制聚合模板时忘改第一行文档，product 包自我介绍成「ACL 权限模块」。功能零影响但文档骗人。**教训**：复制模板后的固定动作——改 docstring、改 import 路径、改变量名，三样过一遍。

---

## Part 7 · 商品分类 — 3 个接口

**日期：** 2026-09-19

### 目标

实现 `API.md` 第 10 章：三级分类的级联查询（10.1 一级全量 / 10.2 按一级查二级 / 10.3 按二级查三级）。全书最短的一章——纯 GET 只读、无请求体、无分页，但它是第 12 章 SPU 的地基（spu 挂 category3_id），且逼出了一个双 ID 模式里最阴险的 bug 形态。

### 操作过程

#### 1. 事实核对先行（本章最重要的发现）

| 事实 | 影响 |
|------|------|
| 三表同构：物理 id + 业务 categoryX_id + name + 父引用列 | 模型照 trademark 模式，Base 供公共列 |
| 行数 17 / 115 / 1099 | 小表全量返回无压力 |
| **category2.category1_id ↔ category1.category1_id 匹配 115/115；↔ 物理 id 只 101/115** | 父子引用走**业务 ID 链**，用物理 id 串链会静默挂错树 |
| category1 物理 id 从 2 开始、业务 ID 从 1 开始，恒错位 1 | 错位来源 |
| category2/3 的物理 id 与业务 ID 恰好对齐 | **掩盖 bug 的帮凶**：只测 10.2→10.3 会误以为物理 id 没问题 |
| spu 表挂 category3_id（业务引用） | 第 12 章前置事实 |

#### 2. 五处改动

- `models/category.py`：三个类一个文件（同一业务的同级实体，拆三个文件是过度组织）
- `crud/category.py`：只读三函数，import 区只有 select——**import 与实际操作一一对应**（Part 6 踩坑 1 的反向应用）
- `schemas/category.py`：无请求体的新形态——第一次出现 Schema 文件里只有序列化
- `routes/product/category.py`：原生 `int` 类型标注（不用 parse_path_int）；Path 参数名自文档化（category1_id 而非 id）
- `routes/product/__init__.py`：聚合追加，**main.py 零改动**——聚合模式红利首次完整兑现

#### 3. 验收方法与结果

27 项断言全过：

- **10.1（6 项）**：17 条、字段恰好 {id, name}、id 值域 1~17（业务 ID 而非物理 2~18）、升序
- **10.2（9 项）**：**全部 17 个一级业务 ID 逐一 id+name 白盒对账**、子数守恒（和 == DB 总数 115）、无挂错树（图书子集 ∩ 手机子集 = 空）、不存在 ID/0 → []、非数字 → 201
- **10.3（5 项）**：抽样 10 个二级业务 ID 逐一白盒对账、字段、category2Id 全等于传参、怪参
- **回归（3 项）**：健康检查、品牌分页五件套、品牌全量（路由顺序，动过 product/__init__.py 必须复验）

### 原理与决策

**引用链准则：跨表引用走哪条 ID 链，接口间传递的 id 就必须是哪条。**

本项目从第一天起响应 id 输出业务 ID（admin_id/role_id/menu_id/tm_id），第 7 章组树走 menu_id 链——当时是讲义直接给的正确答案；本章是数据库值域证据（115/115 vs 101/115）强迫理解为什么。推演挂错树：前端拿图书的物理 id=2 调 getCategory2/2 → WHERE category1_id=2 → 查出手机的子分类——HTTP 200、code=200、数据看起来完全正常，联调都未必能发现。

**为什么 3 个接口而不是 1 棵树？**（对照第 7 章菜单整树）
菜单勾选树打开就要看全树 → 整树返回；商品分类是**级联选择器**——选了「手机」才需要手机的二级，逐级懒加载，每层一个接口参数是父 ID。1099 个三级若整树返回，用户只选个一级却要付整棵树的传输。API 形态跟着交互形态走。

**为什么不用 parse_path_int 兜底？**
分页参数兜底到 1 是无害默认；「父 ID」兜底到 1 = **静默查错分类**，比报错更糟。原生 int + 422 → 全局处理器 → 201（第 5 章老路子）。

**为什么 ID 不存在返回 [] 而非错误？**
查询语义：查无结果不是错误（对照删除语义的幂等静默）。

### 踩坑记录

**1. 验收脚本两处预期错误，且都源于没回读契约原文**

第一轮脚本崩在登录：①密码想当然写 123456——API.md 3.1 请求示例白纸黑字写着 111111；②Token 取法写 data["token"]——契约明写「响应 data：string，JWT Token 字符串」，实现也是 success(token)。两种错法不同、崩点相同：密码错时 data=null 下标访问崩；密码对时 data 是字符串下标访问也崩。

第 5 章踩坑 4（验收脚本也是代码，失败先怀疑预期）的第三次重演，且教训升级：**验收脚本的每个假设都要有出处——契约原文或 DB 事实，想当然写下的预期本身就是未经验证的代码**。

---

## Part 8 · 平台属性管理 — 3 个接口

**日期：** 2026-09-19

### 目标

实现 `API.md` 第 11 章：11.1 属性列表（嵌套属性值）/ 11.2 保存属性（**一个接口两用**）/ 11.3 删除属性。与第 10 章「三个接口干一件事的三个层级」对称，本章是「**一个接口干两件事**」——新增/修改合并在 saveAttrInfo，判据是 id 哨兵值。

### 操作过程

#### 1. 事实核对先行

| 事实 | 影响 |
|------|------|
| 表 attr + attr_value（主子一对多），双 ID 模式延续（attr_id / attr_value_id 雪花） | 模型两类一文件 |
| **attr_value.attr_id ↔ attr.attr_id 匹配 18/18；↔ 物理 id 匹配 0/18** | 引用链铁证：物理链一条都挂不上（比 category 的 101/115 更极端） |
| attr_name 无唯一索引，契约未写「不能重复」 | 不查重（menu 先例） |
| 存量 5 属性全部 category_id=61（「手机」）、category_level 恒 3 | 契约示例值与存量互证 |
| **sku_attr_value 引用 attr.attr_id 与 attr_value.attr_value_id，但冗余存 attr_name/value_name** | 快照语义——删属性/换值后 SKU 数据依然自洽，不级联（品牌删除同构决策） |
| sale_attr 系列表独立存在 | 本章不碰（第 12/13 章 SPU 销售属性的地盘） |

#### 2. 三处改动

- `models/attr.py`：attr + attr_value 两类一文件（同一业务域）；category_level 映射 SmallInteger（DB 实际 tinyint，读回都是 int）
- `crud/attr.py`：六函数正好是四种语义的教科书陈列——查询（平铺 + 分组两函数）、读单个、创建（主子同插）、替换（改主删插子）、删除（先子后主）
- `schemas/attr.py`：**零值哨兵** `id: int = 0`（不传与显式传 0 天然归一）；值条目的 id 字段「接住但忽略」（整体覆盖下值行全换新，旧 ID 不复用）
- `routes/product/attr.py`：11.1 的 c1/c2 只接不查（attr 表只挂末级分类）；11.2 幂等静默分支
- `routes/product/__init__.py`：聚合追加（这次按字母序）

#### 3. 验收方法与结果

39 项断言全过（**一次通过**，登录段直接用第 10 章固化的事实：密码 111111、token 取 data 本身）：

- **11.1 白盒对账（11 项）**：61 分类 5 属性 id/attrName/categoryId/level + 嵌套值列表逐一对账；**id 为雪花业务链（显式断言与物理 1~5 不相交）**；值的 attrId 全等于所属属性；**假 c1/c2 上下文不影响查询（只接不查的正面验证）**
- **11.2 全生命周期（12 项）**：新建→查回→改名换值→**老值行全部消失、新值全新雪花 ID、传来的旧值 ID 被忽略（整体覆盖的直接证据）**→值清空→值空属性在
- **11.3 级联（3 项）**：删测试属性双表零残留、幂等
- **怪参 + 存量保护 + 回归（13 项）**：缺 attrName/categoryLevel 越界 → 201、不存在 id 静默、**attr 表总数回到基线 + 61 分类原封不动**、健康检查/分类/品牌回归

### 原理与决策

**一个接口两用：UPSERT 的契约级表达。**
传统 REST 新增 POST /save、修改 PUT /update 分开；但编辑表单场景下前端不区分新建/编辑（表单结构一样，只是有无 id），契约把两个动作压进一个接口，判据是 id。实现选**零值哨兵**而非「字段在不在」：契约写「不传**或为 0**」——前端可能显式传 id=0（表单初始值），哨兵天然归一两种情况。

**整体覆盖：replace 语义第三次登场。**
先例 replace_user_roles / replace_role_menus，本章是最典型形态：主表 UPDATE + 子表全删全插，同一事务一次 commit。推论：前端传的 attrValueList[].id 是废数据，唯一正确处理是接住、忽略。

**sku_attr_value 的快照语义：为什么断引用不致命。**
它冗余存了 value_name——SKU 生成时把当时的属性值文字抄了一份，此后平台属性怎么改都影响不到 SKU 展示。**关联表与快照表是两种东西**：前者引用丢失即数据残废，后者本来就是为丢失引用设计的。

**组值：第 7 章组树算法的平铺迁移。**
「一次查全表 + 字典分组 + O(1) 取值」在树上叫组树、平铺叫分组——同一个模式。本章 2 次查询代替 N+1 的 1+N 次。

**双 ID 的又一红利：主子同插不需要 flush。**
attr_id 是应用层生成的雪花，子行插入不依赖数据库生成的自增键；若靠物理 id 关联就得先 flush 拿 id。

### 踩坑记录

本章验收一次通过、无踩坑。唯一值得记录的是上章教训的正面兑现：登录段密码与 token 取法直接采用已核实事实书写，省去两轮诊断——**踩过的坑只有写进记忆并复用，才算没白踩**。

---

## 附录 · FastAPI 概念补充

> 本节持续累积 FastAPI / SQLAlchemy / Python 后端开发中遇到的概念笔记，不占 Part 序号，始终置于文档末尾。

### 小节目录

- [A.1 Python 包与 \_\_init\_\_.py](#a1-python-包与-__init__py)
- [A.2 雪花算法（Snowflake）主键](#a2-雪花算法snowflake主键)
- [A.3 pydantic-settings 的取值机制](#a3-pydantic-settings-的取值机制)
- [A.4 自定义异常与 super().\_\_init\_\_(message)](#a4-自定义异常与-super__init__message)
- [A.5 JWT（JSON Web Token）的结构与校验](#a5-jwtjson-web-token的结构与校验)
- [A.6 HTTP 200 的产出链路：成功走默认值，失败走 fail()](#a6-http-200-的产出链路成功走默认值失败走-fail)
- [A.7 FastAPI 依赖注入（Depends）与请求级缓存](#a7-fastapi-依赖注入depends与请求级缓存)
- [A.8 Starlette 路由匹配：先到先得与 FULL / PARTIAL](#a8-starlette-路由匹配先到先得与-full--partial)
- [A.9 app.mount 与 StaticFiles：三个 static 与静态资源访问链路](#a9-appmount-与-staticfiles三个-static-与静态资源访问链路)

### A.1 Python 包与 `__init__.py`

Python 靠 `__init__.py` 识别一个文件夹是「包」（package）而非普通目录。没有它，`from app.config import settings` 会报 `ImportError`。

`__init__.py` 的两个作用：

1. **标记包身份** — 即使是空文件，也能让 Python 识别目录为包
2. **控制对外接口** — 在 `__init__.py` 中 `from .settings import settings`，外部就可以用 `from app.config import settings` 这种简短写法，而不用写完整路径 `from app.config.settings import settings`

> Python 3.3+ 有「命名空间包」概念，理论上不强制要 `__init__.py`，但那适用于跨多目录分散的包。正常项目约定俗成就是加上，避免意外。

### A.2 雪花算法（Snowflake）主键

分布式系统中生成全局唯一 ID 的经典方案，产物是一个 64 位整数。给主键选 ID 策略时通常有三种选择：数据库自增、UUID、雪花算法。

**64 位结构：**

| 位段 | 位数 | 作用 |
|------|------|------|
| 符号位 | 1 | 固定为 0（保证是正数） |
| 时间戳 | 41 | 毫秒级，可用约 69 年 |
| 机器号 | 10 | 5 位数据中心 + 5 位工作机器，最多 1024 个节点 |
| 序列号 | 12 | 同一毫秒内自增，单机每毫秒最多生成 4096 个 |

**三种 ID 方案对比：**

| 维度 | 雪花算法 | 自增 ID | UUID |
|------|---------|---------|------|
| 分布式唯一 | 多实例/分库分表天然不冲突 | 依赖单库，分表需改造 | 唯一但无序 |
| 索引友好 | 趋势递增（高位是时间戳），B+ 树插入友好 | 最好 | 随机写，页分裂严重 |
| 生成时机 | **应用层生成，insert 前就能拿到** | insert 后回查 | 应用层 |
| 信息安全 | 不暴露业务规模 | 竞对可估算订单量 | 不暴露 |
| 性能 | 本地生成，单机每毫秒 4096 个 | 依赖数据库 | 本地生成 |

对电商项目最实际的两个好处：

1. **应用层预生成** — 下单时可以先拿到订单 ID 去做关联、写日志、返回前端，不用等数据库往返
2. **不泄露业务量** — 自增 ID 意味着「第 100000 号订单 = 卖了 10 万单」，雪花 ID 看不出这个信息

**代价与坑：**

- **时钟回拨** — 依赖系统时间，服务器 NTP 对时回拨可能生成重复 ID，需要处理策略（等待 / 报错 / 备用位）
- **workerId 管理** — 多实例部署要保证机器号唯一，要么写死配置，要么用注册中心分配
- **前端精度坑** — 雪花 ID 是 64 位整数，超过 JS 的 `Number.MAX_SAFE_INTEGER`（2^53-1），JSON 返回给前端（Vue 项目）时**末尾几位会被截断**，必须序列化为**字符串**返回（Java 版硅谷甄选在 `JsonConfig` 里做的就是这件事）

**在 SQLAlchemy 中落地：**

```python
from sqlalchemy import BigInteger

def gen_id() -> int:
    # 雪花生成器（可用 snowflake-id 库或自行实现）
    return next_snowflake_id()

id: Mapped[int] = mapped_column(BigInteger, primary_key=True, default=gen_id)
```

- 用 `default=`（Python 层生成）而不是 `autoincrement`
- 类型必须用 `BigInteger`（记得从 `sqlalchemy` 导入），`Integer` 存不下 64 位
- Pydantic 响应模型里要把 ID 字段声明为 `str`，返回前端时才不会丢精度

**本项目取舍：**

单实例学习项目用 MySQL 自增最简单，功能上完全够用；雪花算法的价值在多实例、分库分表等分布式场景才体现。Java 版硅谷甄选用 MyBatis-Plus，其主键策略 `ASSIGN_ID` 默认就是雪花算法，如果要和课程设计对齐，引入是有合理性的。

### A.3 pydantic-settings 的取值机制

`settings.py` 里 `JWT_SECRET_KEY: str` 只写了类型注解、没有赋值，为什么照样能读出 `.env` 里的值？

**核心结论：字段那一行是「字段声明」，不是赋值语句；真正的读取 + 赋值发生在 `Settings()` 实例化那一刻**，由 `BaseSettings` 统一完成：

```python
settings = Settings()   # ← 就是这一刻，逐个字段去外部来源找值
```

**三个要件（缺一不可）：**

1. **继承 `BaseSettings`** — 实例化逻辑被换成“去找值”，而不是“用类里写的值”
2. **`model_config` 里的 `env_file`** — 指定 `.env` 文件的位置
3. **字段名就是键名** — 拿 `JWT_SECRET_KEY` 去对同名条目，默认大小写不敏感

**取值优先级（从高到低，找到即停）：**

```
Settings(...) 显式传入的参数
  → 系统环境变量（os.environ）
    → .env 文件
      → 字段默认值（最后一层兜底）
```

**三种写法的含义：**

| 写法 | 含义 |
|------|------|
| `JWT_SECRET_KEY: str` | 必填：所有外部来源都找不到时，实例化直接抛 `ValidationError` 拒绝启动（fail fast） |
| `JWT_ALGORITHM: str = "HS256"` | 选填：外部没给就用兜底值 |
| `DATABASE_URL: str = "...your_password..."` | 选填 + 占位默认值；`.env` 里的真实值会**覆盖**它 |

> 关键理解：默认值不是“主要来源”，只是兜底的最后一层——`DATABASE_URL` 写着 `your_password` 占位符，实际连的却是 `.env` 里的真实地址，就是这套优先级在起作用。

**两个验证实验（实测输出）：**

```python
# 实验 1：先设置系统环境变量，再加载配置
import os
os.environ["JWT_SECRET_KEY"] = "demo-override"
# → env takes priority: True    （环境变量优先于 .env，把 .env 的值压下去了）

# 实验 2：实例化时用 _env_file=None 关掉 .env 这一层来源
Settings(_env_file=None)
# → ValidationError: JWT_SECRET_KEY  Field required   （没有来源 = 拒绝启动）
```

**顺带完成类型转换和校验：** `.env` 里所有值本质都是字符串，pydantic 按注解转换后再赋值：`DEBUG=true` → `True`（bool）、`JWT_EXPIRE_MINUTES=1200` → `1200`（int）；填了非法值在启动时就报错，不会拖到运行时才炸。

**踩坑：不要写 `env("JWT_SECRET_KEY")`**

`env()` 是 Django（django-environ）风格的 API，pydantic-settings 里不存在这个函数，这样写会在 import 时直接 `NameError` 导致应用起不来。在 pydantic-settings 里，“读取环境变量”的正确表达是**不写默认值**——不写即为必填，读取交给实例化那一刻代劳。

### A.4 自定义异常与 `super().__init__(message)`

`BizException` 的 `__init__` 最后一行 `super().__init__(self.message)` 的作用：把 message “登记”给父类 `Exception`，存入异常的 `args` 属性——之后 `str(e)`、traceback 打印、日志库显示异常时用的就是它。

**不调这行会怎样（不报错，但显示不对）：**

Python 的 `BaseException.__new__` 会先把**构造时传入的原始参数**塞进 `args`；不调 `super` 的话，`args` 一直留着原始参数，而不是解析出来的 `message`。实测对比：

```python
# 类 A：不调 super    →  str(a) = "203"，a.args = (203,)
# 类 B：调了 super    →  str(b) = "nf"， b.args = ('nf',)
```

对照到 `BizException`：

| 抛出方式 | 不调 `super().__init__` | 调了 |
|----------|------------------------|------|
| `BizException(203)` | `str(e)` = `"203"`（裸错误码） | `"用户名不存在"`（解析出的默认提示） |
| `BizException(204, "密码错误")` | `str(e)` = `"(204, '密码错误')"`（元组长相，很难看） | `"密码错误"` |

**为什么项目里重要：**

- 全局异常处理器读的是 `exc.code` / `exc.message` 自定义属性——这部分**不依赖**这行，删了接口也能返回正确内容
- 但异常如果没被处理器接住（如中间件、依赖注入阶段抛出），冒泡到 FastAPI/uvicorn 层时，日志里打的就是 `str(exc)`——有这行才能看到“用户名不存在”，否则只有个 “203”
- `logger.exception()`、调试 traceback 同理；这也是自定义异常的通用规范：自己的字段之外，把 message 交给父类，兼容 `e.args`、序列化等标准行为

**`__init__` 三行的分工：**

```python
self.code = code                  # 自定义字段：业务状态码，给处理器用
self.message = ...                # 自定义字段：解析出的提示，给处理器用
super().__init__(self.message)    # 登记给父类：给 str(e) / traceback / 日志用
```

### A.5 JWT（JSON Web Token）的结构与校验

JWT 是一个由点号分隔的三段式字符串：`header.payload.signature`。

| 段 | 内容 | 说明 |
|----|------|------|
| header | `{"alg": "HS256", "typ": "JWT"}` | Base64URL 编码，声明签名算法 |
| payload | `{"user_id": 1, "exp": 1758...}` | Base64URL 编码，**不是加密**——任何人都能解开查看 |
| signature | 签名值 | 用密钥对前两段计算，防篡改 |

**校验机制（HS256 对称签名）：**

- 签发：服务器用密钥对 `header.payload` 计算签名
- 校验：收到 Token 后用同一密钥重算签名并比对——任何一段被改动，签名都对不上
- 过期：`exp`（UTC 秒时间戳）小于当前时间即失效
- 在 PyJWT 中，签名错误与过期都继承自 `jwt.PyJWTError`，统一捕获即可（本项目 → 206 无效的 Token）

**三个安全要点：**

1. **载荷 ≠ 保险箱**：只放非敏感的业务标识（本项目只放 `user_id`），绝不放密码、密钥等
2. **`algorithms` 白名单**：`jwt.decode()` 必须显式传 `algorithms=["HS256"]`，防算法混淆攻击
3. **密钥保密**：HS256 的安全性完全依赖密钥，泄露意味着任何人都能伪造 Token（密钥放 `.env`、不提交 Git）

**时区坑（本项目实测）：** `exp` 必须用 `datetime.now(timezone.utc)` 计算。naive 本地时间（UTC+8）会被按 UTC 解释，Token 凭空多出 8 小时有效期；验收时专门断言「exp 与真实时间误差 < 60 秒」来兜住此坑。

### A.6 HTTP 200 的产出链路：成功走默认值，失败走 fail()

一个自然的问题：成功响应里的 `HTTP/1.1 200 OK`，到底是在哪行代码写入的？追溯源码后结论是——**成功的 200 项目代码里一个字都没写，是 Starlette 默认参数兜的底；失败的 200 才是 `fail()` 里显式写的**（其实删掉也一样是 200，写着是为了表明设计意图）。以下基于本项目环境实测溯源（FastAPI 0.115.0 / Starlette 0.38.6）。

**成功路径：四步溯源**

① 项目代码没写状态码：`@router.post("/login")` 没传 `status_code` 参数，`success()` 只返回一个普通 dict

② FastAPI 负责包装（`fastapi/routing.py`）：发现返回值不是 `Response` 对象，就用默认响应类 `JSONResponse` 包装；由于装饰器没传、依赖注入也没设置，FastAPI 内部先用空 Response 占位并把它的 `status_code` 抹成 `None`（`fastapi/dependencies/utils.py`）表示「没人指定过」，于是包装时**不传** status_code：

```python
current_status_code = status_code if status_code else solved_result.response.status_code  # None 兜 None → None
if current_status_code is not None:       # 不成立，不添加
    response_args["status_code"] = current_status_code
response = actual_response_class(content, **response_args)   # 包装时不传 status_code
```

③ Starlette 默认参数兜底（`starlette/responses.py`）——**200 真正的出生地**：

```python
class JSONResponse(Response):
    def __init__(self, content, status_code: int = 200, ...):  # ★ 默认值 200
        super().__init__(content, status_code, ...)            # Response.__init__: self.status_code = status_code
```

④ 发送响应时（同文件 `Response.__call__`）：

```python
await send({"type": "http.response.start", "status": self.status_code, ...})  # ★ 200 从这里发出
```

uvicorn 收到 `status=200` 后，渲染成客户端看到的 `HTTP/1.1 200 OK` 状态行。

**失败路径对比：** 失败不是 return，而是 `raise BizException(203)` → 被全局异常处理器接住（`app/api/exception_handlers.py`）→ 调 `fail(203, ...)` → 手动构造 `JSONResponse(status_code=200, content={...})` → 同样走上面第 ④ 步发出去。

| | 成功 | 失败 |
|------|------|------|
| 项目代码里 200 在哪 | **没写**（框架默认值） | `fail()` 里显式写，删掉也还是 200 |
| Response 谁构造 | FastAPI 自动把 dict 包装成 JSONResponse | `fail()` 手动构造 |
| 200 来自哪 | Starlette `JSONResponse` 的默认参数 | 传入的参数 |
| 汇合点 | `starlette/responses.py` 的 `send({"status": ...})` → uvicorn | 同左 |

**为什么路由层看不到 `fail()` 调用？**

`index.py` 里 `raise BizException(203)` 之后就不管了，`fail()` 是在异常处理器里被调用的——这是刻意的解耦：路由层只表达「业务失败了」（raise），失败怎么变成规范响应全交给全局处理器。好处有两个：① 四个处理器（BizException / 参数校验 / HTTP 异常 / 兜底）共用 `fail()` 一个出口，错误格式绝对统一；② `raise` 可以从任意内层（如后续的 CRUD 层）冒出，不必在每个出错点手动 `return fail(...)`。所以 `index.py` 的 import 里只有 `success`，没有 `fail`。

**想改成功响应的 HTTP 状态码？** 在装饰器上传即可：`@router.post("/login", status_code=201)`，FastAPI 会优先采用装饰器传入的值。本项目约定「永远 200」，所以都不传。

### A.7 FastAPI 依赖注入（Depends）与请求级缓存

`get_current_user` 本质上是一个**依赖**（dependency）：一个普通函数，用 `Depends(...)` 声明后，FastAPI 会在调用路由函数之前自动执行它，并把返回值注入进路由参数。

**依赖可以套依赖——「依赖链」自动解析：**

```
get_info(user=Depends(get_current_user), db=Depends(get_db))
  └─ get_current_user(token=Header("Token"), db=Depends(get_db))
       └─ get_db() → SessionLocal() → yield session
```

路由只需声明自己需要什么，FastAPI 递归装配整条链；链上任何一环抛异常（如 207 / 206），请求就终止在那里，路由函数根本不会被调用。

**请求级缓存：同一个依赖函数，在一次请求内只执行一次。**

`get_info` 和 `get_current_user` 都声明了 `Depends(get_db)`，但 `get_db` 在一次请求中只被执行一次——两边拿到的是**同一个 session**，所以「依赖里查用户、端点里再查角色菜单」共享同一连接与事务上下文，不会多开连接。如需关闭该行为，可显式传 `Depends(get_db, use_cache=False)`；本项目保持默认。

**Header 参数：让参数值来自请求头**

```python
token: str | None = Header(default=None, alias="Token", description="登录后获取的 Token")
```

- `Header(...)` 声明该参数从**请求头**取值（与 Query / Body 同为参数来源之一）
- `alias="Token"` 指定请求头名——变量名与头名不一致时使用（变量叫 token，头名按文档约定叫 Token）；HTTP 头大小写不敏感，前端用小写 `token` 一样能收到
- `default=None` 让头缺失时值为 `None`，而不是被 FastAPI 直接判 422；把「没带 Token → 207」的裁决权留在依赖函数内部

### A.8 Starlette 路由匹配：先到先得与 FULL / PARTIAL

FastAPI 的底层是 Starlette，路由匹配算法是**按注册顺序逐条尝试**（`starlette/routing.py`）：

1. 每个路由先做**路径匹配**，路径匹配的再比 HTTP 方法
2. **路径 + 方法都匹配（FULL）→ 立即采用，停止遍历**
3. 路径匹配、方法不符（PARTIAL）→ 先记到一边，继续往后找 FULL
4. 翻完全部路由都没有 FULL → 用记下的 PARTIAL 报 405（本项目被全局处理器统一转成 209）

**推论 1：通配路由会「贪吃」。** `GET /{page}/{limit}`（`str` 宽松匹配 = 任何一段文本都收）是 FULL，会吃掉一切「两段路径 + GET」的请求——包括本意属于其他路由的。本项目实测：`GET /remove/123`（本意走 DELETE 删除接口）被通配接走，返回了用户分页数据。

**推论 2：只有「找不到任何 FULL」时才轮到 405。** `POST /remove/123`：通配是 GET 吃不下、其他路由也没有 FULL → 才用 PARTIAL（`/remove/{id}` 路径匹配但方法不符）报 405 → 209。

**迷你实验**（两条同样路径的路由，交换注册顺序）：

```
通配在前：GET /toAssign/123  → 被 /{page}/{limit} 接走（page="toAssign"）
静态在前：GET /toAssign/123  → 命中 toAssign 路由，返回角色数据
```

**本项目纪律：静态在前、通配最后。** 凡是与通配「同形状」（路径段数相同 + 方法相同）的具体路由，必须注册在通配之前——`user.py` 的 `GET /toAssign/{adminId}` 与通配同为「两段 + GET」，属重点防范对象。

### A.9 app.mount 与 StaticFiles：三个 static 与静态资源访问链路

`main.py` 末行的 `app.mount("/static", StaticFiles(directory="static"), name="static")`：三个 `static` 拼写相同，但分属**三个互不绑定的独立参数**：

| 位置 | 参数 | 所属空间 | 作用 |
|------|------|----------|------|
| ① | `"/static"` | 网址空间 | 挂载点：请求 URL 里匹配的前缀，**必须有**前导 `/` |
| ② | `directory="static"` | 磁盘空间 | 文件从哪里取，相对路径（相对进程工作目录＝项目根），**不能有**前导 `/` |
| ③ | `name="static"` | 命名空间 | 仅供 `request.url_for("static", ...)` 反向生成 URL 与调试认人，不参与匹配和文件查找（签名默认 `None`，可省略） |

**三者互相独立（本项目实测）：** 故意写成 `app.mount("/assets", StaticFiles(directory="static"), name="files")`——请求 `/assets/xxx` 照样命中 `static/` 目录里的文件；`url_for("files", path=...)` 按 URL 前缀生成 `/assets/...`；路由表里登记为 `('/assets', 'files')`。三者同名只是本项目为可读性做的「惯例对齐」。

**映射的本质是「前缀规则」，不是「登记表」：**

- 挂载规则：凡以 `/static` 开头的请求，剥掉前缀，按剩余相对路径到磁盘 `static/` 目录**现场查文件**——找到就返回文件本身，找不到就报 404（被全局处理器包装成 209）
- 上传端（`file_upload.py`）把文件写到 `static/img/sph/...`，返回 `/api/static/img/sph/...` 形状的 URL——两侧没有任何「注册」动作，全靠**共享同一个基准目录 `static/`** 这条约定自动对齐
- 实测佐证：绕过上传接口、直接往磁盘扔一个文件，URL 立即可访问；删掉文件，URL 立即失效——零登记、无状态，因此两者**永远不需要同步什么**

**完整访问链路（注意 `/api` 在哪一段被处理）：**

```
上传落盘:       static/img/sph/20260919/365-1-logo.png
接口返回 URL:   /api/static/img/sph/20260919/365-1-logo.png
                  ↑ 这一段后端自己根本不认识！
浏览器 → 前端开发服务器: 代理见到 /api 就剥掉，转发给后端
后端真实收到:   /static/img/sph/20260919/365-1-logo.png
挂载点剥 /static → 按 img/sph/... 现场查磁盘 → 返回文件
```

实测对照：同一文件用 `/api/static/...` 直接打后端 → `body.code = 209`；用 `/static/...` 打 → 200 返回文件原文。所以 `/api` 是前端代理的「暗号」，不是后端路由；`file_upload.py` 返回的地址是**给前端用**的形状。

**与「HTTP 恒 200」约定的交汇（呼应 A.6）：** 访问不存在的文件、或未经代理直打 `/api/...`，HTTP 状态码**都是 200**，只有 `body.code = 209`（请求路径不存在）能区分成败——静态 404 也会被 `StarletteHTTPException` 处理器统一包装。因此图片被删后，`<img>` 拿到的是 209 的 JSON，前端表现为**裂图**而非 404 页面。

**四个易踩点：**

1. **斜杠方向相反**：①必须有 `"/static"`；②必须无 `"static"`（写成 `"/static"` 会突变成盘符根目录，如 `C:\static`，文件全部找不到）
2. **必须在项目根启动 uvicorn**：②的相对路径与上传端 `Path("static/img/sph")` 都以进程工作目录为基准，换目录启动就会「存到 A、却去 B 找」
3. **`static/` 不入库、启动自举**：该目录被 `.gitignore` 忽略（运行时产物），而 `StaticFiles` 又拒绝不存在的目录，故 `app.mount` 之前有一行 `Path("static").mkdir(exist_ok=True)` 兜底，保证干净机器一次启动成功
4. **`static/` 下一切文件都是公开可访问的**：任何文件 URL 可达，切勿存放敏感内容

**联动改动表（改哪个参数，要连带改什么）：**

| 改哪个 | 直接后果 | 必须连带修改 |
|--------|----------|--------------|
| ① URL 前缀 | 所有图片 URL 前缀变化 | `file_upload.py` 返回串、前端代理剥离规则、库中存量 `logoUrl` |
| ② 磁盘目录 | 从别的文件夹取文件 | 上传端 `UPLOAD_DIR`，否则「存 A 找 B」 |
| ③ name | 仅影响 `url_for` 的引用处 | 无（本项目当前零引用，纯预留） |
