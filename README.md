# 硅谷甄选商城管理系统 · 后端

> FastAPI + SQLAlchemy 2.0 + MySQL 的商城管理系统后端 API

---

## 学习笔记目录

| Part | 主题 | 日期 | 状态 |
|------|------|------|------|
| Part 1 | 项目初始化 — 骨架搭建 | 2026-09-16 | 已完成 |

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

## 附录 · FastAPI 概念补充

> 本节持续累积 FastAPI / SQLAlchemy / Python 后端开发中遇到的概念笔记，不占 Part 序号，始终置于文档末尾。

### 小节目录

- [A.1 Python 包与 \_\_init\_\_.py](#a1-python-包与-__init__py)

### A.1 Python 包与 `__init__.py`

Python 靠 `__init__.py` 识别一个文件夹是「包」（package）而非普通目录。没有它，`from app.config import settings` 会报 `ImportError`。

`__init__.py` 的两个作用：

1. **标记包身份** — 即使是空文件，也能让 Python 识别目录为包
2. **控制对外接口** — 在 `__init__.py` 中 `from .settings import settings`，外部就可以用 `from app.config import settings` 这种简短写法，而不用写完整路径 `from app.config.settings import settings`

> Python 3.3+ 有「命名空间包」概念，理论上不强制要 `__init__.py`，但那适用于跨多目录分散的包。正常项目约定俗成就是加上，避免意外。
