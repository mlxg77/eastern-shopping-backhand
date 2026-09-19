"""
平台属性管理路由
对应接口文档第 11 章：平台属性管理
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.crud import attr as attr_crud
from app.models.user import User
from app.schemas.attr import AttrSaveRequest, attr_to_dict
from app.utils.response import success

router = APIRouter(prefix="/admin/product", tags=["平台属性管理"])


@router.get("/attrInfoList/{c1_id}/{c2_id}/{c3_id}")
def get_attr_info_list(
    c1_id: int,
    c2_id: int,
    c3_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """按三级分类查询属性及属性值（11.1）；c1/c2 为级联选择器上下文，查询只用 c3"""
    attrs = attr_crud.get_attrs_by_category3_id(db, c3_id)
    values_map = attr_crud.get_values_by_attr_ids(db, [a.attr_id for a in attrs])
    return success(
        [attr_to_dict(a, values_map.get(a.attr_id, [])) for a in attrs]
    )


@router.post("/saveAttrInfo")
def save_attr_info(
    payload: AttrSaveRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """保存属性（11.2，一个接口两用）：id=0 新增；携带 id 整体覆盖（值先删后插全换新）"""
    value_names = [v.valueName for v in payload.attrValueList]
    if payload.id == 0:
        attr_crud.create_attr(
            db,
            attr_name=payload.attrName,
            category_id=payload.categoryId,
            category_level=payload.categoryLevel,
            value_names=value_names,
        )
    else:
        # 契约未定义"修改不存在的属性"，按幂等处理：查不到即静默成功
        target = attr_crud.get_attr_by_attr_id(db, payload.id)
        if target is not None:
            attr_crud.replace_attr(
                db,
                target,
                attr_name=payload.attrName,
                category_id=payload.categoryId,
                category_level=payload.categoryLevel,
                value_names=value_names,
            )
    return success()


@router.delete("/deleteAttr/{attr_id}")
def remove_attr(
    attr_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除属性（11.3）：级联清 attr_value；不存在的 ID 静默成功（幂等）"""
    attr_crud.delete_attr(db, attr_id)
    return success()