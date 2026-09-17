"""
模型基类模块
所有 SQLAlchemy 模型都继承自 Base
"""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    声明式基类
    所有业务模型继承此类，自动获得 id、create_time、update_time 字段
    """
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    create_time: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), comment="创建时间"
    )
    update_time: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间"
    )