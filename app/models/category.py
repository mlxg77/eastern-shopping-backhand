"""
商品分类模型模块
映射数据库 category1 / category2 / category3 三张表（三级分类）
"""

from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Category1(Base):
    """一级分类模型"""

    __tablename__ = "category1"

    category1_id: Mapped[int] = mapped_column(BigInteger, comment="一级分类业务ID")
    name: Mapped[str] = mapped_column(String(255), comment="分类名称")


class Category2(Base):
    """二级分类模型"""

    __tablename__ = "category2"

    category2_id: Mapped[int] = mapped_column(BigInteger, comment="二级分类业务ID")
    name: Mapped[str] = mapped_column(String(255), comment="分类名称")
    category1_id: Mapped[int] = mapped_column(BigInteger, comment="所属一级分类业务ID")


class Category3(Base):
    """三级分类模型"""

    __tablename__ = "category3"

    category3_id: Mapped[int] = mapped_column(BigInteger, comment="三级分类业务ID")
    name: Mapped[str] = mapped_column(String(255), comment="分类名称")
    category2_id: Mapped[int] = mapped_column(BigInteger, comment="所属二级分类业务ID")