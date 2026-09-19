"""
ACL 角色管理路由
对应接口文档第 6 章：角色管理
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.crud import role as role_crud
from app.models.user import User
from app.exceptions import BizCode, BizException
from app.schemas.role import RoleSaveRequest, RoleUpdateRequest, role_to_dict
from app.utils.parse import parse_path_int
from app.utils.response import success

router = APIRouter(prefix="/admin/acl/role", tags=["角色管理"])

@router.post("/save")
def save_role(
    payload: RoleSaveRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """新增角色；角色名重复返回 201（契约未定义专属码，用通用参数错误+明确提示）"""
    # 1. 角色名查重（竞态由 DB 唯一索引 idx_role_name 兜底，撞索引走全局 205）
    if role_crud.get_role_by_role_name(db, payload.roleName) is not None:
        raise BizException(BizCode.PARAM_ERROR, "角色名已存在")

    # 2. 入库（业务 ID 由 crud 内部用雪花算法生成）
    role_crud.create_role(db, role_name=payload.roleName, remark=payload.remark)
    return success()


@router.put("/update")
def update_role(
    payload: RoleUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新角色；契约未定义"角色不存在"，按幂等处理：查不到即静默成功"""
    target = role_crud.get_role_by_role_id(db, payload.id)
    if target is not None:
        role_crud.update_role(db, target, role_name=payload.roleName, remark=payload.remark)
    return success()


@router.delete("/remove/{id}")
def remove_role(
    id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除角色；连带清理 user_role / role_menu 两张关联表（幂等）"""
    role_crud.delete_role(db, id)
    return success()

@router.get("/{page}/{limit}")
def get_role_page(
    page: str,
    limit: str,
    roleName: str | None = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取角色分页列表；roleName 可选，按角色名模糊搜索"""
    # 1. 路径参数容错：非法值按 page=1、limit=10 兜底（API.md 2.4 约定）
    page_num = parse_path_int(page, 1)
    limit_num = parse_path_int(limit, 10)

    # 2. 分页查角色 + 统计总数
    roles, total = role_crud.get_role_page(db, page_num, limit_num, roleName)

    # 3. 组装统一分页结构（API.md 2.4）
    return success(
        {
            "records": [role_to_dict(r) for r in roles],
            "total": total,
            "size": limit_num,
            "current": page_num,
            "pages": (total + limit_num - 1) // limit_num,
        }
    )