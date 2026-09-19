"""
菜单数据访问模块
封装 menu、role_menu、user_role 表的数据库操作
"""

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.menu import Menu
from app.models.role import RoleMenu, UserRole
from app.utils.snowflake import snowflake


def get_menus_by_user_id(db: Session, user_id: int) -> list[Menu]:
    """查询用户拥有的全部菜单（含按钮），跨角色去重"""
    return list(
        db.execute(
            select(Menu)
            .join(RoleMenu, RoleMenu.menu_id == Menu.menu_id)
            .join(UserRole, UserRole.role_id == RoleMenu.role_id)
            .where(UserRole.user_id == user_id)
            .distinct()
        ).scalars().all()
    )

def get_all_menus(db: Session) -> list[Menu]:
    """查询全部菜单（按 menu_id 升序：组树后同级节点顺序稳定）"""
    return list(db.execute(select(Menu).order_by(Menu.menu_id)).scalars().all())


def get_menu_by_menu_id(db: Session, menu_id: int) -> Menu | None:
    """按业务 ID 查询菜单，不存在返回 None"""
    return db.execute(
        select(Menu).where(Menu.menu_id == menu_id)
    ).scalar_one_or_none()


def get_menu_by_name(db: Session, name: str) -> Menu | None:
    """按名称查询菜单（查重用）"""
    # menu.name 无唯一索引，同名可能多条——必须 limit(1)+first()，
    # 不能用 scalar_one_or_none()（命中多条会抛 MultipleResultsFound）
    return db.execute(
        select(Menu).where(Menu.name == name).limit(1)
    ).scalars().first()


def has_children(db: Session, menu_id: int) -> bool:
    """判断该菜单下是否还有子节点（7.4 删除前置校验）"""
    stmt = select(Menu.id).where(Menu.pid == menu_id).limit(1)
    return db.execute(stmt).scalars().first() is not None


def create_menu(db: Session, name: str, pid: int, code: str, type: int, level: int) -> Menu:
    """新增菜单：业务 ID 用雪花算法现场生成"""
    menu = Menu(
        menu_id=snowflake.next_id(),
        pid=pid,
        name=name,
        code=code,
        to_code="",   # 列 NOT NULL 且无默认；契约 7.2 未提供 toCode，置空串对齐存量
        type=type,
        status="",    # 列 NOT NULL 且无默认；63 条存量全为空串
        level=level,
    )
    db.add(menu)
    db.commit()
    return menu


def update_menu(db: Session, target: Menu, name: str, pid: int, code: str, level: int) -> None:
    """更新菜单基础信息（契约 7.3 仅定义 name/pid/code/level 四字段）"""
    target.name = name
    target.pid = pid
    target.code = code
    target.level = level
    db.commit()


def delete_menu(db: Session, menu_id: int) -> None:
    """删除菜单；连带清理 role_menu 关联，菜单不存在时无操作（幂等）"""
    db.execute(delete(RoleMenu).where(RoleMenu.menu_id == menu_id))
    db.execute(delete(Menu).where(Menu.menu_id == menu_id))
    db.commit()


def get_menu_ids_by_role_id(db: Session, role_id: int) -> set[int]:
    """查询角色已分配的菜单 ID 集合（7.5 回显勾选；set 天然去重，role_menu 存在重复行）"""
    return set(
        db.execute(
            select(RoleMenu.menu_id).where(RoleMenu.role_id == role_id)
        ).scalars().all()
    )


def replace_role_menus(db: Session, role_id: int, menu_ids: list[int]) -> None:
    """全量覆盖角色菜单：先清空旧关联，再插入新关联（空列表=清空）"""
    db.execute(delete(RoleMenu).where(RoleMenu.role_id == role_id))
    if menu_ids:
        db.add_all([RoleMenu(role_id=role_id, menu_id=mid) for mid in menu_ids])
    db.commit()