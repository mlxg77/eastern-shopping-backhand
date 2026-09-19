"""
角色数据访问模块
封装 role、user_role 表的数据库操作
"""

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.models.role import Role, RoleMenu, UserRole
from app.utils.snowflake import snowflake

def get_role_names_by_user_id(db: Session, user_id: int) -> list[str]:
    """查询用户拥有的角色名列表"""
    return list(
        db.execute(
            select(Role.role_name)
            .join(UserRole, UserRole.role_id == Role.role_id)
            .where(UserRole.user_id == user_id)
        ).scalars().all()
    )

def get_role_names_map_by_user_ids(
    db: Session, user_ids: list[int]
) -> dict[int, list[str]]:
    """
    批量查询多个用户的角色名
    :return: {user_id: [角色名, ...]}，无角色的用户不在字典里
    """
    if not user_ids:
        return {}
    rows = db.execute(
        select(UserRole.user_id, Role.role_name)
        .join(Role, Role.role_id == UserRole.role_id)
        .where(UserRole.user_id.in_(user_ids))
    ).all()
    result: dict[int, list[str]] = {}
    for user_id, role_name in rows:
        result.setdefault(user_id, []).append(role_name)
    return result

def get_all_roles(db: Session) -> list[Role]:
    """查询系统中全部角色（按角色 ID 排序）"""
    return list(db.execute(select(Role).order_by(Role.role_id)).scalars().all())

def get_roles_by_user_id(db: Session, user_id: int) -> list[Role]:
    """查询某用户已分配的角色"""
    return list(
        db.execute(
            select(Role)
            .join(UserRole, UserRole.role_id == Role.role_id)
            .where(UserRole.user_id == user_id)
            .order_by(Role.role_id)
        ).scalars().all()
    )

def replace_user_roles(db: Session, user_id: int, role_ids: list[int]) -> None:
    """全量覆盖用户角色：先清空旧关联，再插入新关联（空列表=清空）"""
    db.execute(delete(UserRole).where(UserRole.user_id == user_id))
    if role_ids:
        db.add_all([UserRole(user_id=user_id, role_id=rid) for rid in role_ids])
    db.commit()

def get_role_page(
    db: Session,
    page: int,
    limit: int,
    role_name: str | None = None,
) -> tuple[list[Role], int]:
    """
    分页查询角色列表
    :return: (当前页角色列表, 总记录数)
    """
    # 总数统计（与列表共用同一套筛选条件）
    count_stmt = select(func.count()).select_from(Role)
    # 数据查询：按业务 role_id 显式排序，保证跨页稳定
    list_stmt = select(Role).order_by(Role.role_id)
    # 可选条件：按角色名模糊搜索
    if role_name:
        count_stmt = count_stmt.where(Role.role_name.like(f"%{role_name}%"))
        list_stmt = list_stmt.where(Role.role_name.like(f"%{role_name}%"))

    total = db.execute(count_stmt).scalar_one()
    roles = list(
        db.execute(list_stmt.offset((page - 1) * limit).limit(limit))
        .scalars()
        .all()
    )
    return roles, total

def get_role_by_role_id(db: Session, role_id: int) -> Role | None:
    """按业务 ID 查询角色，不存在返回 None"""
    return db.execute(
        select(Role).where(Role.role_id == role_id)
    ).scalar_one_or_none()

def get_role_by_role_name(db: Session, role_name: str) -> Role | None:
    """按角色名查询角色（唯一索引保证至多一条），不存在返回 None"""
    return db.execute(
        select(Role).where(Role.role_name == role_name)
    ).scalar_one_or_none()

def create_role(db: Session, role_name: str, remark: str | None) -> Role:
    """新增角色：业务 ID 用雪花算法现场生成，提交后返回实体"""
    role = Role(
        role_id=snowflake.next_id(),
        role_name=role_name,
        remark=remark,
    )
    db.add(role)
    db.commit()
    return role


def update_role(db: Session, target: Role, role_name: str, remark: str | None) -> None:
    """更新角色基础信息（角色名、备注）"""
    target.role_name = role_name
    target.remark = remark
    db.commit()


def delete_role(db: Session, role_id: int) -> None:
    """
    删除角色
    连带清理 user_role、role_menu 两张关联表；角色不存在时无操作（幂等）
    """
    # 先清两张关联表，再删角色本体（同一事务，一次提交）
    db.execute(delete(UserRole).where(UserRole.role_id == role_id))
    db.execute(delete(RoleMenu).where(RoleMenu.role_id == role_id))
    db.execute(delete(Role).where(Role.role_id == role_id))
    db.commit()