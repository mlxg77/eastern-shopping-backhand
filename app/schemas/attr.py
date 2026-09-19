"""
平台属性模块 Schema
保存属性请求体结构（新增/修改两用），以及 Attr / AttrValue 实体的序列化
"""

from pydantic import BaseModel, Field

from app.models.attr import Attr, AttrValue


class AttrValueItem(BaseModel):
    """保存请求里的属性值条目"""

    valueName: str = Field(min_length=1, max_length=255)
    id: int = 0  # 契约可不传；整体覆盖策略下值行全换新，此字段接住但忽略


class AttrSaveRequest(BaseModel):
    """保存属性请求体：id=0（不传或显式 0）新增，携带 id 修改"""

    id: int = 0
    attrName: str = Field(min_length=1, max_length=255)
    categoryId: int = Field(ge=1)
    categoryLevel: int = Field(ge=1, le=4)
    attrValueList: list[AttrValueItem] = Field(default_factory=list)


def attr_value_to_dict(v: AttrValue) -> dict:
    """AttrValue 实体 -> 契约属性值结构（id/valueName/attrId）"""
    return {
        "id": v.attr_value_id,
        "valueName": v.value_name,
        "attrId": v.attr_id,
    }


def attr_to_dict(attr: Attr, values: list[AttrValue]) -> dict:
    """Attr 实体 + 其属性值列表 -> 契约属性结构（id/attrName/categoryId/categoryLevel/attrValueList）"""
    return {
        "id": attr.attr_id,
        "attrName": attr.attr_name,
        "categoryId": attr.category_id,
        "categoryLevel": attr.category_level,
        "attrValueList": [attr_value_to_dict(v) for v in values],
    }