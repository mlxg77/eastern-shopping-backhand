"""
用户数据访问模块
封装 user 表的数据库操作
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


def get_user_by_username(db: Session, username: str) -> User | None:
    """按用户名查询用户，不存在返回 None"""
    return db.execute(
        select(User).where(User.username == username)
    ).scalar_one_or_none()