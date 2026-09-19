"""
SPU 管理路由
对应接口文档第 12 章：SPU 管理（分页 / 增改删 / 基础销售属性）

路由顺序红线：/{page}/{limit} 是 product 域根级两段 GET 通配，
必须注册在本文件所有 GET 路由之后；本模块必须在 category 之后聚合注册。
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.crud import spu as spu_crud
from app.models.user import User
from app.schemas.spu import SpuSaveRequest, SpuUpdateRequest, sale_attr_to_dict, spu_to_dict
from app.utils.parse import parse_path_int
from app.utils.response import page_result, success

router = APIRouter(prefix="/admin/product", tags=["SPU管理"])


@router.get("/spu/list")
def spu_list_legacy(
    page: str = Query(default="1"),
    size: str = Query(default="10"),
    limit: str | None = Query(default=None),
    category3_id: int = Query(..., alias="category3Id"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """旧路径兼容（12.1 括注）：分页走 Query，参数名 size/limit 均可（limit 优先）"""
    page_num = parse_path_int(page, 1)
    limit_num = parse_path_int(limit if limit is not None else size, 10)
    spus, total = spu_crud.get_spu_page(db, category3_id, page_num, limit_num)
    return success(page_result([spu_to_dict(s) for s in spus], total, page_num, limit_num))


@router.get("/baseSaleAttrList")
def get_base_sale_attr_list(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取全部基础销售属性（12.5）"""
    return success([sale_attr_to_dict(a) for a in spu_crud.get_all_sale_attrs(db)])


@router.post("/saveSpuInfo")
def save_spu_info(
    payload: SpuSaveRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """新增 SPU（12.2）：主表 + 图片 + 销售属性 + 属性值四表同一事务"""
    spu_crud.create_spu(
        db,
        spu_name=payload.spuName,
        description=payload.description,
        category3_id=payload.category3Id,
        tm_id=payload.tmId,
        images=[(img.imgName, img.imgUrl) for img in payload.spuImageList],
        sale_attrs=[
            (
                attr.baseSaleAttrId,
                attr.saleAttrName,
                [v.saleAttrValueName for v in attr.spuSaleAttrValueList],
            )
            for attr in payload.spuSaleAttrList
        ],
    )
    return success()


@router.post("/updateSpuInfo")
def update_spu_info(
    payload: SpuUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新 SPU（12.3）：整体覆盖（图片列表、销售属性以本次提交为准）；不存在的 id 幂等静默"""
    target = spu_crud.get_spu_by_spu_id(db, payload.id)
    if target is not None:
        spu_crud.replace_spu(
            db,
            target,
            spu_name=payload.spuName,
            description=payload.description,
            category3_id=payload.category3Id,
            tm_id=payload.tmId,
            images=[(img.imgName, img.imgUrl) for img in payload.spuImageList],
            sale_attrs=[
                (
                    attr.baseSaleAttrId,
                    attr.saleAttrName,
                    [v.saleAttrValueName for v in attr.spuSaleAttrValueList],
                )
                for attr in payload.spuSaleAttrList
            ],
        )
    return success()


@router.delete("/deleteSpu/{id}")
def remove_spu(
    id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除 SPU（12.4）：级联清三张子表（图片/销售属性/属性值）；不存在的 ID 静默（幂等）"""
    spu_crud.delete_spu(db, id)
    return success()


@router.get("/{page}/{limit}")
def get_spu_page(
    page: str,
    limit: str,
    category3_id: int = Query(..., alias="category3Id"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    获取 SPU 分页列表（12.1，新路径）
    ⚠️ 域根级两段 GET 通配：必须保持本文件最后一条路由（spu/list 已在前面注册）
    """
    page_num = parse_path_int(page, 1)
    limit_num = parse_path_int(limit, 10)
    spus, total = spu_crud.get_spu_page(db, category3_id, page_num, limit_num)
    return success(page_result([spu_to_dict(s) for s in spus], total, page_num, limit_num))