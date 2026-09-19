"""
商品分类路由
对应接口文档第 10 章：商品分类（三级级联查询）
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.crud import category as category_crud
from app.models.user import User
from app.schemas.category import (
    category1_to_dict,
    category2_to_dict,
    category3_to_dict,
)
from app.utils.response import success

router = APIRouter(prefix="/admin/product", tags=["商品分类"])


@router.get("/getCategory1")
def get_category1(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取全部一级分类（10.1）"""
    return success([category1_to_dict(c) for c in category_crud.get_all_category1(db)])


@router.get("/getCategory2/{category1_id}")
def get_category2(
    category1_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """按一级分类业务 ID 获取其下二级分类（10.2）；ID 不存在返回空数组"""
    return success(
        [category2_to_dict(c) for c in category_crud.get_category2_by_category1_id(db, category1_id)]
    )


@router.get("/getCategory3/{category2_id}")
def get_category3(
    category2_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """按二级分类业务 ID 获取其下三级分类（10.3）；ID 不存在返回空数组"""
    return success(
        [category3_to_dict(c) for c in category_crud.get_category3_by_category2_id(db, category2_id)]
    )