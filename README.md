# 硅谷甄选商城管理系统 · 后端

> FastAPI + SQLAlchemy 2.0 + MySQL 的商城管理系统后端 API

---

## 学习笔记目录

| Part | 主题 | 日期 | 状态 |
|------|------|------|------|
| Part 1 | 项目初始化 — 骨架搭建 | 2026-09-16 | 已完成 |
| Part 2 | 登录功能 — 公共底座与登录/登出接口 | 2026-09-17 | 已完成 |

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

## Part 2 · 登录功能 — 公共底座与登录/登出接口

**日期：** 2026-09-17

### 目标

对照 `API.md`（共 46 个接口）实现第一个完整功能模块——登录认证（3.1 登录 / 3.2 登出），并借此搭起后续所有接口都要复用的公共底座：统一响应格式、业务异常体系、JWT 签发与校验工具。

### 操作过程

#### 1. 接口盘点与开发顺序决策

盘点 `API.md` 后可以确定：46 个接口里只有 **3.1 登录** 和 **3.2 登出** 不需要 Token，其余接口全部要求请求头携带 Token。登录接口是 Token 的「生产者」——只有先能登录，才拿得到 Token 去调试其他接口，所以它必须最先写。

同时从已建好的数据库（20 张表）确认了三条关键事实：

- **双 ID 模式**：每张表都有 `id`（BIGINT 自增，物理主键，业务不用）和 `xxx_id`（业务 ID，雪花算法生成，接口层一律使用它）；关联表（如 `user_role`）里存的也是业务 ID
- **user 表数据**：`admin` 用户 `user_id=1`，密码 `111111`（明文存储，与种子数据一致）
- **Token 约定**：放在请求头 `Token` 字段（不是 `Authorization: Bearer`），有效期 1200 分钟

#### 2. 开发路线图

按依赖关系拆成 5 步：**① 模型层 → ② JWT 配置 → ③ 统一响应与异常体系 → ④ JWT 工具 → ⑤ 登录/登出接口本体**。前 4 步搭的是公共底座，之后每个接口都会用到。

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

#### 8. 验收方法

用 `TestClient` 加载真实 `app.main` 的应用实例跑断言脚本（临时脚本、跑完即删），覆盖：

- 正常路径：登录成功、Token 三段式、**反解 Token 与数据库对账**（`user_id=1`）
- 错误分支：204 / 203 / 201（缺字段、空 JSON）
- 边界：无 Token 可登录（登录免鉴权）、雪花 ID 用户（`user_id=8804574609536`）正常登录
- 元数据：OpenAPI 中两条路径与「登录认证」tag 齐全
- JWT 工具单独验收：`exp` 与真实时间误差 < 60 秒（兜住时区坑）、篡改 / 过期 / 错误密钥 / 垃圾输入 → 206

三轮验收（JWT 工具 10 项、登录逻辑 16 项、真实应用端到端 10 项，共 36 项断言）全部通过；期间共发现 4 处问题，均已修复（见踩坑记录）。

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

## 附录 · FastAPI 概念补充

> 本节持续累积 FastAPI / SQLAlchemy / Python 后端开发中遇到的概念笔记，不占 Part 序号，始终置于文档末尾。

### 小节目录

- [A.1 Python 包与 \_\_init\_\_.py](#a1-python-包与-__init__py)
- [A.2 雪花算法（Snowflake）主键](#a2-雪花算法snowflake主键)
- [A.3 pydantic-settings 的取值机制](#a3-pydantic-settings-的取值机制)
- [A.4 自定义异常与 super().\_\_init\_\_(message)](#a4-自定义异常与-super__init__message)
- [A.5 JWT（JSON Web Token）的结构与校验](#a5-jwtjson-web-token的结构与校验)
- [A.6 HTTP 200 的产出链路：成功走默认值，失败走 fail()](#a6-http-200-的产出链路成功走默认值失败走-fail)

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
