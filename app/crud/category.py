"""
商品分类数据访问模块
封装 category1 / category2 / category3 表的只读查询
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import Category1, Category2, Category3


def get_all_category1(db: Session) -> list[Category1]:
    """查询全部一级分类（按业务 ID 升序）"""
    return list(db.execute(select(Category1).order_by(Category1.category1_id)).scalars().all())


def get_category2_by_category1_id(db: Session, category1_id: int) -> list[Category2]:
    """按一级分类业务 ID 查询其下二级分类（按业务 ID 升序）"""
    return list(
        db.execute(
            select(Category2)
            .where(Category2.category1_id == category1_id)
            .order_by(Category2.category2_id)
        )
        .scalars()
        .all()
    )


def get_category3_by_category2_id(db: Session, category2_id: int) -> list[Category3]:
    """按二级分类业务 ID 查询其下三级分类（按业务 ID 升序）"""
    return list(
        db.execute(
            select(Category3)
            .where(Category3.category2_id == category2_id)
            .order_by(Category3.category3_id)
        )
        .scalars()
        .all()
    )