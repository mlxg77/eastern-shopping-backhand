"""
SKU 管理路由
对应接口文档第 13 章：SKU 管理（SPU 图片/销售属性查询 / 新增 / 列表 / 详情 / 上下架 / 删除）

本文件全部为具体字面量路径（两段或三段），无通配段，文件内部无顺序依赖；
但聚合层必须注册在 spu 之前——spu 的 GET /{page}/{limit} 是域根级两段通配，
先注册会吞掉本文件的 /spuImageList/{id} 等两段 GET（详见 product/__init__.py）。
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.crud import sku as sku_crud
from app.models.user import User
from app.schemas.sku import (
    SkuSaveRequest,
    sku_to_dict,
    spu_image_to_dict,
    spu_sale_attr_to_dict,
)
from app.utils.response import page_result, success

router = APIRouter(prefix="/admin/product", tags=["SKU管理"])


@router.get("/spuImageList/{id}")
def get_spu_image_list(
    id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取 SPU 图片列表（13.1）：id 为 SPU 业务 ID"""
    return success([spu_image_to_dict(i) for i in sku_crud.get_spu_images(db, id)])


@router.get("/spuSaleAttrList/{id}")
def get_spu_sale_attr_list(
    id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取 SPU 销售属性列表（13.2）：id 为 SPU 业务 ID，值按 sale_attr_id 对齐嵌套"""
    return success(
        [
            spu_sale_attr_to_dict(attr, values)
            for attr, values in sku_crud.get_spu_sale_attrs_with_values(db, id)
        ]
    )


@router.post("/saveSkuInfo")
def save_sku_info(
    payload: SkuSaveRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """新增 SKU（13.3）：主表 + 三张快照子表四表同一事务"""
    sku_crud.create_sku(
        db,
        spu_id=payload.spuID,
        category3_id=payload.category3Id,
        tm_id=payload.tmId,
        sku_name=payload.skuName,
        price=payload.price,
        weight=str(payload.weight),
        sku_desc=payload.skuDesc,
        sku_default_img=payload.skuDefaultImg,
        is_sale=payload.isSale,
        attr_values=[
            (v.attrId, v.valueId, v.valueName, v.attrName)
            for v in payload.skuAttrValueList
        ],
        sale_attr_values=[
            (v.saleAttrId, v.saleAttrValueId, v.saleAttrName, v.saleAttrValueName)
            for v in payload.skuSaleAttrValueList
        ],
        images=[
            (img.imgUrl, img.spuImgId, img.isDefault)
            for img in payload.skuImageList
        ],
    )
    return success()


@router.get("/findBySpuId/{id}")
def find_skus_by_spu_id(
    id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """根据 SPU 查询 SKU 列表（13.4）：完整详情结构数组（含三嵌套）"""
    skus = sku_crud.get_skus_by_spu_id(db, id)
    attr_map, sale_map, image_map = sku_crud.get_sku_children(
        db, [s.sku_id for s in skus]
    )
    return success(
        [
            sku_to_dict(
                s,
                attr_map.get(s.sku_id, []),
                sale_map.get(s.sku_id, []),
                image_map.get(s.sku_id, []),
            )
            for s in skus
        ]
    )


@router.get("/list/{page}/{limit}")
def get_sku_page(
    page: int,
    limit: int,
    spu_id: int | None = Query(None, alias="spuId"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    获取 SKU 分页列表（13.5）：三段字面量路径，与 spu 的两段通配形状不同天然不冲突
    嵌套三列表恒 null（契约 13.5 明文），完整数据走 13.6 详情
    """
    skus, total = sku_crud.get_sku_page(db, page, limit, spu_id)
    return success(
        page_result(
            [sku_to_dict(s, [], [], [], details=False) for s in skus],
            total,
            page,
            limit,
        )
    )


@router.get("/getSkuInfo/{id}")
def get_sku_info(
    id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取 SKU 详情（13.6）：id 为 SKU 业务 ID；不存在的 id 返回 data null"""
    sku = sku_crud.get_sku_by_sku_id(db, id)
    if sku is None:
        return success()
    attr_map, sale_map, image_map = sku_crud.get_sku_children(db, [sku.sku_id])
    return success(
        sku_to_dict(
            sku,
            attr_map.get(sku.sku_id, []),
            sale_map.get(sku.sku_id, []),
            image_map.get(sku.sku_id, []),
        )
    )


@router.get("/onSale/{id}")
def on_sale(
    id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """SKU 上架（13.7）：is_sale 置 1；不存在的 id 幂等静默"""
    sku_crud.set_sku_sale(db, id, 1)
    return success()


@router.get("/cancelSale/{id}")
def cancel_sale(
    id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """SKU 下架（13.7）：is_sale 置 0；不存在的 id 幂等静默"""
    sku_crud.set_sku_sale(db, id, 0)
    return success()


@router.delete("/deleteSku/{id}")
def remove_sku(
    id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除 SKU（13.8）：级联清三张快照子表；不存在的 ID 静默（幂等）"""
    sku_crud.delete_sku(db, id)
    return success()