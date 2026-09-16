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
│   ├── config.py             # pydantic-settings 配置管理
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

#### 3. 配置管理（config.py）

使用 `pydantic-settings` 的 `BaseSettings` 从 `.env` 读取配置，定义三个配置项：

- `APP_NAME` — 应用名称，用于 Swagger 文档标题
- `DEBUG` — 调试开关，控制是否打印 SQL 和自动建表
- `DATABASE_URL` — MySQL 连接字符串，格式为 `mysql+pymysql://用户名:密码@主机:端口/数据库名?charset=utf8mb4`

全局导出 `settings` 单例，其他模块直接 `from app.config import settings` 即可使用。

#### 4. 数据库连接（database.py）

- 用 `create_engine` 创建引擎，配置了连接池（`pool_size=10`，`max_overflow=20`）和 `pool_pre_ping`（连接前检测存活）
- `SessionLocal` 是 Session 工厂，`autocommit=False`、`autoflush=False` 让事务完全手动控制
- `echo=settings.DEBUG`：调试模式下会在终端打印执行的 SQL
- `get_db()` 依赖函数不放在这里，而是统一定义在 `api/deps.py`：`database.py` 只负责基础设施（engine + Session 工厂），路由统一 `from app.api.deps import get_db` 注入 session，请求结束后自动关闭

#### 5. 模型基类（models/base.py）

使用 SQLAlchemy 2.0 的 `DeclarativeBase` 定义基类 `Base`，所有业务模型继承它后自动获得三个字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | `int`，自增主键 | 每条记录的唯一标识 |
| `created_at` | `datetime`，`server_default=func.now()` | 插入时由数据库自动生成 |
| `updated_at` | `datetime`，`onupdate=func.now()` | 每次更新时自动刷新 |

#### 6. 应用入口（main.py）

- 使用 `@asynccontextmanager` 定义 `lifespan` 管理应用生命周期
- 启动时：DEBUG 模式下尝试 `Base.metadata.create_all()` 自动建表，连接失败会打印友好提示而不是崩溃
- 健康检查 `GET /` 返回 `{"status": "ok", "app": "...", "version": "0.1.0"}`
- 预留 `include_router` 注册点，后续业务模块的路由在此挂载

#### 7. Alembic 数据库迁移

- 通过 `alembic init alembic` 初始化迁移目录
- 修改 `alembic/env.py`：导入项目的 `settings` 和 `Base.metadata`，用 `config.set_main_option("sqlalchemy.url", ...)` 覆盖 `alembic.ini` 中的连接字符串
- 后续添加模型后，运行 `alembic revision --autogenerate -m "描述"` 生成迁移脚本，`alembic upgrade head` 执行迁移

#### 8. 环境变量与 Git

- `.env` 存放真实配置，已加入 `.gitignore` 不提交
- `.env.example` 是模板文件，含占位符，提交到 Git 供协作者参考
- `.gitignore` 还忽略了 `__pycache__/`、`.venv/`、IDE 配置等

### 原理与决策

**为什么用 pydantic-settings 而不是直接读 os.environ？**
`BaseSettings` 自动从 `.env` 文件加载环境变量，同时提供类型校验和默认值。比手动 `os.getenv()` + 类型转换更简洁安全。

**为什么用 DeclarativeBase 而不是传统的 declarative_base()？**
`declarative_base()` 是 SQLAlchemy 1.x 风格，2.0 推荐使用 `DeclarativeBase` 类继承方式，配合 `Mapped` 和 `mapped_column` 可以获得完整的类型提示支持。

**为什么在 lifespan 里做自动建表？**
开发阶段频繁调试，自动建表省去了手动跑迁移的步骤。同时加了 try-except，MySQL 没启动时应用依然能跑（只是不能访问数据库接口）。生产环境应关闭 DEBUG 并使用 Alembic 迁移。

**为什么连接池设 pool_size=10、max_overflow=20？**
商城系统初期流量不大，10 个常驻连接 + 20 个临时连接足够应对。后续可根据实际负载调整。

**为什么 charset 用 utf8mb4 而不是 utf8？**
MySQL 的 `utf8` 只支持 3 字节字符，`utf8mb4` 支持 4 字节（包括 emoji 等），是真正的 UTF-8 编码。

### 踩坑记录

**1. MySQL 未启动时应用直接崩溃**

最初 lifespan 中直接调用 `Base.metadata.create_all(bind=engine)`，如果 MySQL 没运行，会抛出 `OperationalError` 导致应用无法启动。加了 try-except 后，连接失败时打印提示信息并跳过建表，应用正常启动，健康检查和 Swagger 文档仍可用。

**2. cryptography 依赖缺失**

PyMySQL 连接 MySQL 8.0+ 时，默认使用 `caching_sha2_password` 认证插件，需要 `cryptography` 库来解密认证信息。如果不装会报 `RuntimeError: 'cryptography' package is required`。已在 `requirements.txt` 中加入。

**3. PowerShell 中文乱码**

在 Windows PowerShell 中通过 `urllib` 测试接口时，返回的中文内容显示为乱码。这是 PowerShell 终端编码问题（默认 GBK），不影响实际 JSON 响应内容，浏览器和 Swagger UI 中显示正常。

---

## 附录 · FastAPI 概念补充

> 本节持续累积 FastAPI / SQLAlchemy / Python 后端开发中遇到的概念笔记，不占 Part 序号，始终置于文档末尾。

### 小节目录

（暂无，后续开发中遇到新概念时补充）
