"""
商品品牌管理路由
对应接口文档第 9 章：品牌管理
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.crud import trademark as trademark_crud
from app.exceptions import BizCode, BizException
from app.models.user import User
from app.schemas.trademark import TrademarkSaveRequest, TrademarkUpdateRequest, trademark_to_dict
from app.utils.parse import parse_path_int
from app.utils.response import page_result, success

router = APIRouter(prefix="/admin/product/baseTrademark", tags=["品牌管理"])


@router.post("/save")
def save_trademark(
    payload: TrademarkSaveRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """新增品牌；品牌名重复返回 201（索引兜底并发竞态，撞 idx_tm_name 走全局 205）"""
    # 1. 品牌名查重
    if trademark_crud.get_trademark_by_tm_name(db, payload.tmName) is not None:
        raise BizException(BizCode.PARAM_ERROR, "品牌名已存在")

    # 2. 入库（业务 ID 由 crud 内部用雪花算法生成）
    trademark_crud.create_trademark(db, tm_name=payload.tmName, logo_url=payload.logoUrl)
    return success()


@router.put("/update")
def update_trademark(
    payload: TrademarkUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新品牌；契约未定义"品牌不存在"，按幂等处理：查不到即静默成功"""
    target = trademark_crud.get_trademark_by_tm_id(db, payload.id)
    if target is not None:
        trademark_crud.update_trademark(db, target, tm_name=payload.tmName, logo_url=payload.logoUrl)
    return success()


@router.delete("/remove/{id}")
def remove_trademark(
    id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除品牌；叶子实体无关联表级联，不存在的 ID 静默成功（幂等）"""
    trademark_crud.delete_trademark(db, id)
    return success()


@router.get("/getTrademarkList")
def get_trademark_list(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取所有品牌（不分页）"""
    trademarks = trademark_crud.get_all_trademarks(db)
    return success([trademark_to_dict(t) for t in trademarks])


@router.get("/{page}/{limit}")
def get_trademark_page(
    page: str,
    limit: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取品牌分页列表（契约未定义搜索参数）"""
    # 1. 路径参数容错：非法值按 page=1、limit=10 兜底（API.md 2.4 约定）
    page_num = parse_path_int(page, 1)
    limit_num = parse_path_int(limit, 10)

    # 2. 分页查品牌 + 统计总数
    trademarks, total = trademark_crud.get_trademark_page(db, page_num, limit_num)

    # 3. 组装统一分页结构（API.md 2.4）
    return success(page_result([trademark_to_dict(t) for t in trademarks], total, page_num, limit_num))