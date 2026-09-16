"""
公共依赖模块
提供路由中常用的依赖注入函数
"""

from typing import Generator

from sqlalchemy.orm import Session

from app.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    数据库 session 依赖
    在路由函数中通过 Depends(get_db) 注入
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
