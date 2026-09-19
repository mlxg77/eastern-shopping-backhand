"""
平台属性数据访问模块
封装 attr / attr_value 表的读写操作
"""

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.attr import Attr, AttrValue
from app.utils.snowflake import snowflake


def get_attrs_by_category3_id(db: Session, category_id: int) -> list[Attr]:
    """按三级分类业务 ID 查询其下属性（按业务 ID 升序）"""
    return list(
        db.execute(
            select(Attr)
            .where(Attr.category_id == category_id, Attr.category_level == 3)
            .order_by(Attr.attr_id)
        )
        .scalars()
        .all()
    )


def get_values_by_attr_ids(db: Session, attr_ids: list[int]) -> dict[int, list[AttrValue]]:
    """
    按属性业务 ID 集合一次查出全部属性值，按所属属性分组
    :return: {attr_id: [AttrValue, ...]}，空入参返回空字典
    """
    if not attr_ids:
        return {}
    rows = db.execute(
        select(AttrValue)
        .where(AttrValue.attr_id.in_(attr_ids))
        .order_by(AttrValue.attr_value_id)
    ).scalars().all()
    result: dict[int, list[AttrValue]] = {}
    for v in rows:
        result.setdefault(v.attr_id, []).append(v)
    return result


def get_attr_by_attr_id(db: Session, attr_id: int) -> Attr | None:
    """按业务 ID 查询属性，不存在返回 None（唯一索引 idx_attr_id 保证至多一条）"""
    return db.execute(
        select(Attr).where(Attr.attr_id == attr_id)
    ).scalar_one_or_none()


def create_attr(
    db: Session,
    attr_name: str,
    category_id: int,
    category_level: int,
    value_names: list[str],
) -> Attr:
    """新增属性及其全部属性值；业务 ID 用雪花算法现场生成，同一事务一次提交"""
    attr = Attr(
        attr_id=snowflake.next_id(),
        attr_name=attr_name,
        category_id=category_id,
        category_level=category_level,
    )
    db.add(attr)
    for value_name in value_names:
        db.add(
            AttrValue(
                attr_value_id=snowflake.next_id(),
                value_name=value_name,
                attr_id=attr.attr_id,
            )
        )
    db.commit()
    return attr


def replace_attr(
    db: Session,
    target: Attr,
    attr_name: str,
    category_id: int,
    category_level: int,
    value_names: list[str],
) -> None:
    """
    整体覆盖属性：主表字段更新 + 属性值先删后插全换新（replace 语义，前端传来的值 ID 不复用）
    """
    target.attr_name = attr_name
    target.category_id = category_id
    target.category_level = category_level
    db.execute(delete(AttrValue).where(AttrValue.attr_id == target.attr_id))
    for value_name in value_names:
        db.add(
            AttrValue(
                attr_value_id=snowflake.next_id(),
                value_name=value_name,
                attr_id=target.attr_id,
            )
        )
    db.commit()


def delete_attr(db: Session, attr_id: int) -> None:
    """
    删除属性：先清亲儿子 attr_value，再删 attr 本体（同一事务）
    sku_attr_value 为快照引用（冗余存名），不级联——品牌删除同构决策
    """
    db.execute(delete(AttrValue).where(AttrValue.attr_id == attr_id))
    db.execute(delete(Attr).where(Attr.attr_id == attr_id))
    db.commit()