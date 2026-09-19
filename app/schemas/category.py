"""
商品分类模块 Schema
Category1 / Category2 / Category3 实体的序列化（本章三个接口均为只读，无请求体）
"""

from app.models.category import Category1, Category2, Category3


def category1_to_dict(c: Category1) -> dict:
    """Category1 实体 -> 契约一级分类结构（id/name）"""
    return {
        "id": c.category1_id,
        "name": c.name,
    }


def category2_to_dict(c: Category2) -> dict:
    """Category2 实体 -> 契约二级分类结构（id/name/category1Id）"""
    return {
        "id": c.category2_id,
        "name": c.name,
        "category1Id": c.category1_id,
    }


def category3_to_dict(c: Category3) -> dict:
    """Category3 实体 -> 契约三级分类结构（id/name/category2Id）"""
    return {
        "id": c.category3_id,
        "name": c.name,
        "category2Id": c.category2_id,
    }