"""
ACL 用户管理路由
对应接口文档第 5 章：用户管理
"""

from datetime import datetime

from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.crud import role as role_crud
from app.crud import user as user_crud
from app.exceptions import BizCode, BizException
from app.models.user import User
from app.schemas.user import DoAssignRoleRequest, UserSaveRequest, UserUpdateRequest
from app.schemas.role import role_to_dict
from app.utils.parse import parse_path_int
from app.utils.response import success

router = APIRouter(prefix="/admin/acl/user", tags=["用户管理"])

def _fmt_time(dt: datetime | None) -> str:
    """时间格式化为 yyyy-MM-dd HH:mm:ss（API.md 2.4 约定）"""
    return dt.strftime("%Y-%m-%d %H:%M:%S") if dt else ""

@router.post("/save")
def save_user(
    payload: UserSaveRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """新增用户；用户名重复返回 202"""
    # 1. 用户名查重（竞态由 DB 唯一索引兜底，撞索引走全局 205）
    if user_crud.get_user_by_username(db, payload.username) is not None:
        raise BizException(BizCode.USERNAME_EXISTS)  # 202

    # 2. 入库（业务 ID 由 crud 内部用雪花算法生成）
    user_crud.create_user(
        db,
        username=payload.username,
        name=payload.name,
        password=payload.password,
    )
    return success()


@router.put("/update")
def update_user(
    payload: UserUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新用户；契约未定义"用户不存在"，按幂等处理：查不到即静默成功"""
    target = user_crud.get_user_by_user_id(db, payload.id)
    if target is not None:
        user_crud.update_user(db, target, username=payload.username, name=payload.name)
    return success()

@router.delete("/remove/{id}")
def remove_user(
    id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除用户；契约未定义"用户不存在"，按幂等处理：静默成功"""
    user_crud.delete_users(db, [id])
    return success()


@router.delete("/batchRemove")
def batch_remove_users(
    ids: list[int] = Body(..., min_length=1, description="用户 ID 数组，不能为空"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """批量删除用户；请求体为 JSON 数组，空数组返回 201"""
    user_crud.delete_users(db, ids)
    return success()

@router.get("/toAssign/{adminId}")
def to_assign(
    adminId: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取用户已分配角色 + 系统全部角色"""
    assign_roles = role_crud.get_roles_by_user_id(db, adminId)
    all_roles = role_crud.get_all_roles(db)
    return success(
        {
            "assignRoles": [role_to_dict(r) for r in assign_roles],
            "allRolesList": [role_to_dict(r) for r in all_roles],
        }
    )


@router.post("/doAssignRole")
def do_assign_role(
    payload: DoAssignRoleRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """为用户分配角色（全量覆盖：提交列表即最终结果，空列表=清空）"""
    role_crud.replace_user_roles(db, payload.userId, payload.roleIdList)
    return success()

@router.get("/{page}/{limit}")
def get_user_page(
    page: str,
    limit: str,
    username: str | None = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取用户分页列表；username 可选，按用户名模糊搜索"""
    # 1. 路径参数容错：非法值按 page=1、limit=10 兜底（API.md 2.4 约定）
    page_num = parse_path_int(page, 1)
    limit_num = parse_path_int(limit, 10)

    # 2. 分页查用户 + 统计总数
    users, total = user_crud.get_user_page(db, page_num, limit_num, username)

    # 3. 一次 IN 查询批量取这些用户的角色名，避免逐行查库（N+1）
    role_map = role_crud.get_role_names_map_by_user_ids(db, [u.user_id for u in users])

    # 4. 组装 records：驼峰字段、时间格式化、多角色逗号拼接
    records = [
        {
            "id": u.user_id,
            "username": u.username,
            "name": u.name,
            "phone": u.phone or "",
            "password": u.password,
            "roleName": ",".join(role_map.get(u.user_id, [])),
            "createTime": _fmt_time(u.create_time),
            "updateTime": _fmt_time(u.update_time),
        }
        for u in users
    ]

    # 5. 组装统一分页结构（API.md 2.4）
    return success(
        {
            "records": records,
            "total": total,
            "size": limit_num,
            "current": page_num,
            "pages": (total + limit_num - 1) // limit_num,
        }
    )
