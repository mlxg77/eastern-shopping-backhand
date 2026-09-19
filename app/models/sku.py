"""
SKU 模型模块
映射数据库 sku / sku_attr_value / sku_sale_attr_value / sku_image 四张表
结构变更（2026-09-19）：四表已 ALTER 补齐 create_time / update_time 列，
与其他业务表统一继承 Base
"""

from sqlalchemy import BigInteger, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Sku(Base):
    """SKU（库存量单位）模型：一个 SPU 的具体可购买规格"""

    __tablename__ = "sku"

    sku_id: Mapped[int] = mapped_column(BigInteger, comment="SKU业务ID")
    spu_id: Mapped[int] = mapped_column(BigInteger, comment="所属SPU业务ID")
    category_3_id: Mapped[int] = mapped_column(BigInteger, comment="三级分类业务ID（DB列名带下划线）")
    tm_id: Mapped[int] = mapped_column(BigInteger, comment="品牌业务ID")
    sku_name: Mapped[str] = mapped_column(String(255), comment="SKU名称")
    weight: Mapped[str] = mapped_column(String(255), comment="重量(克)，varchar存数字字符串")
    price: Mapped[int] = mapped_column(BigInteger, comment="价格(分)")
    sku_desc: Mapped[str] = mapped_column(String(255), comment="SKU描述")
    sku_default_img: Mapped[str] = mapped_column(String(255), comment="默认展示图片URL")
    is_sale: Mapped[int] = mapped_column(SmallInteger, comment="上架状态：0下架 1上架")


class SkuAttrValue(Base):
    """SKU 平台属性快照模型（attr_id/value_id 引平台属性表，名称为冗余快照）"""

    __tablename__ = "sku_attr_value"

    sku_attr_value_id: Mapped[int] = mapped_column(BigInteger, comment="快照行业务ID")
    attr_id: Mapped[int] = mapped_column(BigInteger, comment="平台属性业务ID")
    value_id: Mapped[int] = mapped_column(BigInteger, comment="平台属性值业务ID")
    value_name: Mapped[str] = mapped_column(String(255), comment="属性值名称快照")
    attr_name: Mapped[str] = mapped_column(String(255), comment="属性名称快照")
    sku_id: Mapped[int] = mapped_column(BigInteger, comment="所属SKU业务ID")


class SkuSaleAttrValue(Base):
    """SKU 销售属性值快照模型"""

    __tablename__ = "sku_sale_attr_value"

    sku_sale_attr_value_id: Mapped[int] = mapped_column(BigInteger, comment="快照行业务ID")
    sale_attr_id: Mapped[int] = mapped_column(BigInteger, comment="销售属性业务ID")
    sale_attr_value_id: Mapped[int] = mapped_column(BigInteger, comment="销售属性值业务ID")
    sale_attr_name: Mapped[str] = mapped_column(String(255), comment="销售属性名称快照")
    sale_attr_value_name: Mapped[str] = mapped_column(String(255), comment="销售属性值名称快照")
    sku_id: Mapped[int] = mapped_column(BigInteger, comment="所属SKU业务ID")


class SkuImage(Base):
    """SKU 图片模型（无名称列，imgName 由 image_url 尾段反推）"""

    __tablename__ = "sku_image"

    image_id: Mapped[int] = mapped_column(BigInteger, comment="图片业务ID")
    sku_id: Mapped[int] = mapped_column(BigInteger, comment="所属SKU业务ID")
    image_url: Mapped[str] = mapped_column(String(255), comment="图片URL")
    spu_image_id: Mapped[int] = mapped_column(BigInteger, comment="来源SPU图片业务ID")
    is_default: Mapped[str] = mapped_column(String(1), comment="是否默认图：'1'是 '0'否")