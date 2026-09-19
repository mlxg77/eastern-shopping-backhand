"""
品牌模型模块
映射数据库 trademark 表
"""

from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Trademark(Base):
    """品牌模型"""

    __tablename__ = "trademark"

    tm_id: Mapped[int] = mapped_column(BigInteger, comment="业务品牌ID")
    tm_name: Mapped[str] = mapped_column(String(255), comment="品牌名称")
    logo_url: Mapped[str] = mapped_column(String(255), comment="LOGO 图片 URL")