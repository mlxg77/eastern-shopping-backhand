"""
用户模型模块
映射数据库 user 表
"""

from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class User(Base):
    """管理员用户模型"""

    __tablename__ = "user"

    user_id: Mapped[int] = mapped_column(BigInteger, comment="业务用户ID")
    username: Mapped[str] = mapped_column(String(64), comment="登录用户名")
    password: Mapped[str] = mapped_column(String(64), comment="登录密码")
    name: Mapped[str] = mapped_column(String(64), comment="用户昵称")
    phone: Mapped[str | None] = mapped_column(String(20), comment="手机号")
    avatar: Mapped[str | None] = mapped_column(String(255), comment="头像URL")