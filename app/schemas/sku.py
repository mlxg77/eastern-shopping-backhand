"""
SKU 模块 Schema
保存 SKU 请求体结构（三层子列表），以及 Sku 系实体的序列化
"""

from pydantic import BaseModel, Field

from app.models.sku import Sku, SkuAttrValue, SkuImage, SkuSaleAttrValue
from app.models.spu import SaleAttrValue, SpuImage, SpuSaleAttr
from app.utils.format import fmt_time


class SkuAttrValueItem(BaseModel):
    """保存请求里的平台属性快照条目（字段同契约 13.3）"""

    attrId: int = Field(ge=1)
    valueId: int = Field(ge=1)
    valueName: str = Field(min_length=1, max_length=255)
    attrName: str = Field(min_length=1, max_length=255)


class SkuSaleAttrValueItem(BaseModel):
    """保存请求里的销售属性值快照条目"""

    saleAttrId: int = Field(ge=1)
    saleAttrValueId: int = Field(ge=1)
    saleAttrName: str = Field(min_length=1, max_length=255)
    saleAttrValueName: str = Field(min_length=1, max_length=255)


class SkuImageItem(BaseModel):
    """保存请求里的 SKU 图片条目（imgName 接住但忽略：sku_image 表无名称列）"""

    imgName: str = Field(min_length=1, max_length=255)
    imgUrl: str = Field(min_length=1, max_length=255)
    spuImgId: int = Field(default=0)
    isDefault: str = Field(default="0", pattern="^[01]$")


class SkuSaveRequest(BaseModel):
    """
    新增 SKU 请求体（契约 13.3）
    id/skuId 由服务端生成；price/weight 兼容数字或字符串——
    Pydantic v2 lax 模式下 int 声明天然接受 JSON number 与整数字符串
    """

    spuID: int = Field(ge=1)
    category3Id: int = Field(ge=1)
    tmId: int = Field(ge=1)
    skuName: str = Field(min_length=1, max_length=255)
    price: int = Field(ge=0)
    weight: int = Field(default=0, ge=0)
    skuDesc: str = Field(default="", max_length=255)
    skuDefaultImg: str = Field(min_length=1, max_length=255)
    isSale: int = Field(default=0, ge=0, le=1)
    skuAttrValueList: list[SkuAttrValueItem] = Field(default_factory=list)
    skuSaleAttrValueList: list[SkuSaleAttrValueItem] = Field(default_factory=list)
    skuImageList: list[SkuImageItem] = Field(default_factory=list)


def _weight_to_int(weight: str) -> int:
    """DB weight 列是 varchar 但语义为数字：防御转换，脏值兜 0（序列化不能因一脏值 500）"""
    try:
        return int(weight)
    except ValueError:
        return 0


def spu_image_to_dict(image: SpuImage) -> dict:
    """SpuImage 实体 -> 契约 13.1 结构（id/imgName/imgUrl/spuId）"""
    return {
        "id": image.image_id,
        "imgName": image.image_name,
        "imgUrl": image.image_url,
        "spuId": image.spu_id,
    }


def spu_sale_attr_to_dict(attr: SpuSaleAttr, values: list[SaleAttrValue]) -> dict:
    """SpuSaleAttr + 值列表 -> 契约 13.2 双层嵌套结构"""
    return {
        "id": attr.spu_sale_attr_id,
        "baseSaleAttrId": attr.base_sale_attr_id,
        "saleAttrName": attr.sale_attr_name,
        "spuId": attr.spu_id,
        "spuSaleAttrValueList": [
            {
                "id": v.sale_attr_value_id,
                "saleAttrValueName": v.sale_attr_value_name,
                "baseSaleAttrId": v.sale_attr_id,
                "spuId": v.spu_id,
            }
            for v in values
        ],
    }


def sku_attr_value_to_dict(v: SkuAttrValue) -> dict:
    """SkuAttrValue 实体 -> 契约 13.6 嵌套条目（字段同 13.3）"""
    return {
        "attrId": v.attr_id,
        "valueId": v.value_id,
        "valueName": v.value_name,
        "attrName": v.attr_name,
    }


def sku_sale_attr_value_to_dict(v: SkuSaleAttrValue) -> dict:
    """SkuSaleAttrValue 实体 -> 契约 13.6 嵌套条目（字段同 13.3）"""
    return {
        "saleAttrId": v.sale_attr_id,
        "saleAttrValueId": v.sale_attr_value_id,
        "saleAttrName": v.sale_attr_name,
        "saleAttrValueName": v.sale_attr_value_name,
    }


def sku_image_to_dict(image: SkuImage) -> dict:
    """SkuImage 实体 -> 契约 13.6 嵌套条目（imgName 由 URL 尾段反推：表无名称列）"""
    return {
        "imgName": image.image_url.rsplit("/", 1)[-1],
        "imgUrl": image.image_url,
        "spuImgId": image.spu_image_id,
        "isDefault": image.is_default,
    }


def sku_to_dict(
    sku: Sku,
    attr_values: list[SkuAttrValue],
    sale_attr_values: list[SkuSaleAttrValue],
    images: list[SkuImage],
    *,
    details: bool = True,
) -> dict:
    """
    Sku 实体 -> 契约 13.6 详情结构
    :param details: True 输出完整三嵌套（13.4/13.6）；False 三嵌套恒 None（13.5 契约明文）
    createTime/updateTime：结构变更后表有列，输出 fmt_time 真实时间
    """
    result = {
        "id": sku.sku_id,
        "spuID": sku.spu_id,
        "category3Id": sku.category_3_id,
        "tmId": sku.tm_id,
        "skuName": sku.sku_name,
        "price": sku.price,
        "weight": _weight_to_int(sku.weight),
        "skuDesc": sku.sku_desc,
        "skuDefaultImg": sku.sku_default_img,
        "isSale": sku.is_sale,
        "createTime": fmt_time(sku.create_time),
        "updateTime": fmt_time(sku.update_time),
    }
    if details:
        result["skuAttrValueList"] = [sku_attr_value_to_dict(v) for v in attr_values]
        result["skuSaleAttrValueList"] = [
            sku_sale_attr_value_to_dict(v) for v in sale_attr_values
        ]
        result["skuImageList"] = [sku_image_to_dict(i) for i in images]
    else:
        result["skuAttrValueList"] = None
        result["skuSaleAttrValueList"] = None
        result["skuImageList"] = None
    return result