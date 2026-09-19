"""
品牌数据访问模块
封装 trademark 表的数据库操作
"""

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.models.trademark import Trademark
from app.utils.snowflake import snowflake


def get_trademark_page(db: Session, page: int, limit: int) -> tuple[list[Trademark], int]:
    """
    分页查询品牌列表
    :return: (当前页品牌列表, 总记录数)
    """
    count_stmt = select(func.count()).select_from(Trademark)
    list_stmt = select(Trademark).order_by(Trademark.tm_id)

    total = db.execute(count_stmt).scalar_one()
    trademarks = list(
        db.execute(list_stmt.offset((page - 1) * limit).limit(limit))
        .scalars()
        .all()
    )
    return trademarks, total


def get_all_trademarks(db: Session) -> list[Trademark]:
    """查询全部品牌（不分页，按 tm_id 升序）"""
    return list(db.execute(select(Trademark).order_by(Trademark.tm_id)).scalars().all())


def get_trademark_by_tm_id(db: Session, tm_id: int) -> Trademark | None:
    """按业务 ID 查询品牌，不存在返回 None"""
    return db.execute(
        select(Trademark).where(Trademark.tm_id == tm_id)
    ).scalar_one_or_none()


def get_trademark_by_tm_name(db: Session, tm_name: str) -> Trademark | None:
    """按品牌名查询品牌（唯一索引 idx_tm_name 保证至多一条），不存在返回 None"""
    return db.execute(
        select(Trademark).where(Trademark.tm_name == tm_name)
    ).scalar_one_or_none()


def create_trademark(db: Session, tm_name: str, logo_url: str) -> Trademark:
    """新增品牌：业务 ID 用雪花算法现场生成，提交后返回实体"""
    trademark = Trademark(
        tm_id=snowflake.next_id(),
        tm_name=tm_name,
        logo_url=logo_url,
    )
    db.add(trademark)
    db.commit()
    return trademark


def update_trademark(db: Session, target: Trademark, tm_name: str, logo_url: str) -> None:
    """更新品牌基础信息（品牌名、LOGO URL）"""
    target.tm_name = tm_name
    target.logo_url = logo_url
    db.commit()


def delete_trademark(db: Session, tm_id: int) -> None:
    """删除品牌；品牌不存在时无操作（幂等）。无关联表级联（tm 为叶子实体，spu.tm_id 是业务引用，契约未定义拦截）"""
    db.execute(delete(Trademark).where(Trademark.tm_id == tm_id))
    db.commit()