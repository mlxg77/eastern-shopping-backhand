"""
SPU 模型模块
映射数据库 spu / spu_image_list / spu_sale_attr / sale_attr / sale_attr_value 五张表
"""

from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Spu(Base):
    """SPU（标准产品单元）模型"""

    __tablename__ = "spu"

    spu_id: Mapped[int] = mapped_column(BigInteger, comment="SPU业务ID")
    spu_name: Mapped[str] = mapped_column(String(255), comment="SPU名称")
    description: Mapped[str] = mapped_column(String(255), comment="SPU描述")
    category3_id: Mapped[int] = mapped_column(BigInteger, comment="三级分类业务ID")
    tm_id: Mapped[int] = mapped_column(BigInteger, comment="品牌业务ID")


class SpuImage(Base):
    """SPU 图片模型"""

    __tablename__ = "spu_image_list"

    image_id: Mapped[int] = mapped_column(BigInteger, comment="图片业务ID")
    image_name: Mapped[str] = mapped_column(String(255), comment="图片名称")
    image_url: Mapped[str] = mapped_column(String(255), comment="图片URL")
    spu_id: Mapped[int] = mapped_column(BigInteger, comment="所属SPU业务ID")


class SpuSaleAttr(Base):
    """SPU 销售属性模型"""

    __tablename__ = "spu_sale_attr"

    spu_sale_attr_id: Mapped[int] = mapped_column(BigInteger, comment="SPU销售属性业务ID")
    base_sale_attr_id: Mapped[int] = mapped_column(BigInteger, comment="基础销售属性业务ID")
    sale_attr_name: Mapped[str] = mapped_column(String(255), comment="销售属性名称")
    spu_id: Mapped[int] = mapped_column(BigInteger, comment="所属SPU业务ID")


class SaleAttr(Base):
    """基础销售属性模型（全局字典表）"""

    __tablename__ = "sale_attr"

    sale_attr_id: Mapped[int] = mapped_column(BigInteger, comment="基础销售属性业务ID")
    sale_attr_name: Mapped[str] = mapped_column(String(255), comment="销售属性名称")


class SaleAttrValue(Base):
    """SPU 销售属性值模型（sale_attr_id 引基础属性表，与 spu_sale_attr 是兄弟非父子）"""

    __tablename__ = "sale_attr_value"

    sale_attr_value_id: Mapped[int] = mapped_column(BigInteger, comment="销售属性值业务ID")
    sale_attr_value_name: Mapped[str] = mapped_column(String(255), comment="销售属性值名称")
    sale_attr_id: Mapped[int] = mapped_column(BigInteger, comment="基础销售属性业务ID")
    spu_id: Mapped[int] = mapped_column(BigInteger, comment="所属SPU业务ID")