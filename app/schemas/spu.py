"""
SPU 模块 Schema
保存 SPU 请求体结构（双层嵌套），以及 Spu / SaleAttr 实体的序列化
"""

from pydantic import BaseModel, Field

from app.models.spu import SaleAttr, Spu
from app.utils.format import fmt_time


class SpuImageItem(BaseModel):
    """保存请求里的 SPU 图片条目（imgName/imgUrl -> DB image_name/image_url）"""

    imgName: str = Field(min_length=1, max_length=255)
    imgUrl: str = Field(min_length=1, max_length=255)


class SpuSaleAttrValueItem(BaseModel):
    """保存请求里的销售属性值条目"""

    saleAttrValueName: str = Field(min_length=1, max_length=255)
    baseSaleAttrId: int = Field(ge=1)


class SpuSaleAttrItem(BaseModel):
    """保存请求里的销售属性条目"""

    baseSaleAttrId: int = Field(ge=1)
    saleAttrName: str = Field(min_length=1, max_length=255)
    spuSaleAttrValueList: list[SpuSaleAttrValueItem] = Field(default_factory=list)


class SpuSaveRequest(BaseModel):
    """新增 SPU 请求体（契约：id/spuId/createTime/updateTime 服务端生成，传了被忽略）"""

    spuName: str = Field(min_length=1, max_length=255)
    description: str = Field(default="", max_length=255)
    category3Id: int = Field(ge=1)
    tmId: int = Field(ge=1)
    spuImageList: list[SpuImageItem] = Field(default_factory=list)
    spuSaleAttrList: list[SpuSaleAttrItem] = Field(default_factory=list)


class SpuUpdateRequest(SpuSaveRequest):
    """更新 SPU 请求体：新增结构 + 必传 id（整体覆盖）"""

    id: int = Field(ge=1)


def spu_to_dict(spu: Spu) -> dict:
    """Spu 实体 -> 契约分页 records 元素（id/spuName/description/category3Id/tmId/createTime/updateTime）"""
    return {
        "id": spu.spu_id,
        "spuName": spu.spu_name,
        "description": spu.description,
        "category3Id": spu.category3_id,
        "tmId": spu.tm_id,
        "createTime": fmt_time(spu.create_time),
        "updateTime": fmt_time(spu.update_time),
    }


def sale_attr_to_dict(attr: SaleAttr) -> dict:
    """SaleAttr 实体 -> 契约结构（id/name）"""
    return {
        "id": attr.sale_attr_id,
        "name": attr.sale_attr_name,
    }