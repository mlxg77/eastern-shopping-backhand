"""
ACL 权限（菜单）管理路由
对应接口文档第 7 章：权限（菜单）管理
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.crud import menu as menu_crud
from app.exceptions import BizCode, BizException
from app.models.user import User
from app.schemas.menu import MenuSaveRequest, MenuUpdateRequest, build_menu_tree
from app.utils.response import success

router = APIRouter(prefix="/admin/acl/permission", tags=["权限管理"])


@router.get("")
def get_menu_tree(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取全部菜单树；select 恒 False（勾选回显是 7.5 的事）"""
    menus = menu_crud.get_all_menus(db)
    return success(build_menu_tree(menus))


@router.post("/save")
def save_menu(
    payload: MenuSaveRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """新增菜单；名称重复返回 201（契约括注「不能与已有菜单重复」）"""
    # 1. 名称查重（menu.name 无唯一索引，无并发兜底，竞态窗口如实存在）
    if menu_crud.get_menu_by_name(db, payload.name) is not None:
        raise BizException(BizCode.PARAM_ERROR, "菜单名已存在")

    # 2. 入库（业务 ID 由 crud 内部用雪花算法生成）
    menu_crud.create_menu(
        db,
        name=payload.name,
        pid=payload.pid,
        code=payload.code,
        type=payload.type,
        level=payload.level,
    )
    return success()


@router.put("/update")
def update_menu(
    payload: MenuUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新菜单；契约未定义"菜单不存在"，按幂等处理：查不到即静默成功"""
    target = menu_crud.get_menu_by_menu_id(db, payload.id)
    if target is not None:
        menu_crud.update_menu(
            db, target, name=payload.name, pid=payload.pid, code=payload.code, level=payload.level
        )
    return success()


@router.delete("/remove/{id}")
def remove_menu(
    id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除菜单；该节点下有子节点返回 208（BizCode.MENU_HAS_CHILDREN 首次启用）"""
    if menu_crud.has_children(db, id):
        raise BizException(BizCode.MENU_HAS_CHILDREN)  # 208
    menu_crud.delete_menu(db, id)
    return success()


@router.get("/toAssign/{roleId}")
def to_assign(
    roleId: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取全量菜单树并回显该角色已勾选的节点（select=True）"""
    menus = menu_crud.get_all_menus(db)
    selected = menu_crud.get_menu_ids_by_role_id(db, roleId)
    return success(build_menu_tree(menus, selected))


@router.post("/doAssign")
def do_assign(
    roleId: int,
    permissionId: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """给角色分配权限（全量覆盖）；参数走 URL Query，permissionId 是逗号分隔的菜单 ID 串"""
    # 1. 解析逗号分隔的 ID：过滤空段；非法数字 → 201；保序去重防 role_menu 重复行
    try:
        menu_ids = [int(x) for x in permissionId.split(",") if x.strip()]
    except ValueError:
        raise BizException(BizCode.PARAM_ERROR, "permissionId 含非法数字")
    menu_ids = list(dict.fromkeys(menu_ids))

    # 2. 全量覆盖角色-菜单关联（空列表 = 清空）
    menu_crud.replace_role_menus(db, roleId, menu_ids)
    return success()