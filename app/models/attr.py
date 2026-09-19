"""
平台属性模型模块
映射数据库 attr / attr_value 两张表（主子一对多）
"""

from sqlalchemy import BigInteger, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Attr(Base):
    """平台属性模型"""

    __tablename__ = "attr"

    attr_id: Mapped[int] = mapped_column(BigInteger, comment="属性业务ID")
    attr_name: Mapped[str] = mapped_column(String(255), comment="属性名称")
    category_id: Mapped[int] = mapped_column(BigInteger, comment="所属分类业务ID（三级）")
    category_level: Mapped[int] = mapped_column(SmallInteger, comment="分类级别（DB 实际为 tinyint，存量恒 3）")


class AttrValue(Base):
    """平台属性值模型"""

    __tablename__ = "attr_value"

    attr_value_id: Mapped[int] = mapped_column(BigInteger, comment="属性值业务ID")
    value_name: Mapped[str] = mapped_column(String(255), comment="属性值名称")
    attr_id: Mapped[int] = mapped_column(BigInteger, comment="所属属性业务ID")