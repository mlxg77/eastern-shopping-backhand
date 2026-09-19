"""
用户数据访问模块
封装 user 表的数据库操作
"""

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.models.role import UserRole
from app.models.user import User
from app.utils.snowflake import snowflake


def get_user_by_username(db: Session, username: str) -> User | None:
    """按用户名查询用户，不存在返回 None"""
    return db.execute(
        select(User).where(User.username == username)
    ).scalar_one_or_none()

def get_user_by_user_id(db: Session, user_id: int) -> User | None:
    """按业务 ID 查询用户，不存在返回 None"""
    return db.execute(
        select(User).where(User.user_id == user_id)
    ).scalar_one_or_none()

def get_user_page(
    db: Session,
    page: int,
    limit: int,
    username: str | None = None,
) -> tuple[list[User], int]:
    """
    分页查询用户列表
    :return: (当前页用户列表, 总记录数)
    """
    # 总数统计（与列表共用同一套筛选条件）
    count_stmt = select(func.count()).select_from(User)
    # 数据查询：显式排序，保证跨页稳定
    list_stmt = select(User).order_by(User.user_id)
    # 可选条件：按用户名模糊搜索
    if username:
        count_stmt = count_stmt.where(User.username.like(f"%{username}%"))
        list_stmt = list_stmt.where(User.username.like(f"%{username}%"))

    total = db.execute(count_stmt).scalar_one()
    users = list(
        db.execute(list_stmt.offset((page - 1) * limit).limit(limit))
        .scalars()
        .all()
    )
    return users, total

def create_user(db: Session, username: str, name: str, password: str) -> User:
    """新增用户：业务 ID 用雪花算法现场生成，提交后返回实体"""
    user = User(
        user_id=snowflake.next_id(),
        username=username,
        name=name,
        password=password,
    )
    db.add(user)
    db.commit()
    return user


def update_user(db: Session, target: User, username: str, name: str) -> None:
    """更新用户基础信息（用户名、昵称）"""
    target.username = username
    target.name = name
    db.commit()

def delete_users(db: Session, user_ids: list[int]) -> None:
    """
    批量删除用户（含单个删除）
    同时清理 user_role 中的角色关联；不存在的 ID 静默忽略（幂等）
    """
    if not user_ids:
        return
    # 先清关联表，再删用户本体（同一事务，一次提交）
    db.execute(delete(UserRole).where(UserRole.user_id.in_(user_ids)))
    db.execute(delete(User).where(User.user_id.in_(user_ids)))
    db.commit()