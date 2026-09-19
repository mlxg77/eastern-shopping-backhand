"""
模型包
统一导出所有模型，供 Alembic 自动发现
"""

from app.models.attr import Attr, AttrValue
from app.models.base import Base
from app.models.category import Category1, Category2, Category3
from app.models.menu import Menu
from app.models.role import Role, RoleMenu, UserRole
from app.models.sku import Sku, SkuAttrValue, SkuImage, SkuSaleAttrValue
from app.models.spu import SaleAttr, SaleAttrValue, Spu, SpuImage, SpuSaleAttr
from app.models.user import User

__all__ = [
    "Attr",
    "AttrValue",
    "Base",
    "Category1",
    "Category2",
    "Category3",
    "Menu",
    "Role",
    "RoleMenu",
    "SaleAttr",
    "SaleAttrValue",
    "Sku",
    "SkuAttrValue",
    "SkuImage",
    "SkuSaleAttrValue",
    "Spu",
    "SpuImage",
    "SpuSaleAttr",
    "User",
    "UserRole",
]