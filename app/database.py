"""
数据库连接模块
创建 SQLAlchemy 引擎和 Session 工厂
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,       # 连接前 ping 一下，防止断开连接
    pool_size=10,             # 连接池大小
    max_overflow=20,          # 超出连接池大小时允许额外创建的连接数
    echo=False,              # SQL 日志由 logging_config 统一控制
)

# Session 工厂
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)
