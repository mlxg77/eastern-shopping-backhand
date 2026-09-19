"""
SPU 数据访问模块
封装 spu 及其三张子表（图片 / 销售属性 / 属性值）的读写操作
"""

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.models.spu import SaleAttr, SaleAttrValue, Spu, SpuImage, SpuSaleAttr
from app.utils.snowflake import snowflake


def get_spu_page(
    db: Session, category3_id: int, page: int, limit: int
) -> tuple[list[Spu], int]:
    """按三级分类分页查询 SPU：return (当前页列表, 总数)"""
    count_stmt = select(func.count()).select_from(Spu).where(Spu.category3_id == category3_id)
    list_stmt = (
        select(Spu)
        .where(Spu.category3_id == category3_id)
        .order_by(Spu.spu_id)
    )
    total = db.execute(count_stmt).scalar_one()
    spus = list(
        db.execute(list_stmt.offset((page - 1) * limit).limit(limit)).scalars().all()
    )
    return spus, total


def get_spu_by_spu_id(db: Session, spu_id: int) -> Spu | None:
    """按业务 ID 查询 SPU（spu_id 无唯一索引，limit(1) 保证多行不炸）"""
    return db.execute(
        select(Spu).where(Spu.spu_id == spu_id).limit(1)
    ).scalars().first()


def get_all_sale_attrs(db: Session) -> list[SaleAttr]:
    """查询全部基础销售属性（按业务 ID 升序）"""
    return list(
        db.execute(select(SaleAttr).order_by(SaleAttr.sale_attr_id)).scalars().all()
    )


def _delete_spu_children(db: Session, spu_id: int) -> None:
    """删除 SPU 的三张子表数据（图片 / 销售属性 / 属性值），供删除与整体覆盖复用"""
    db.execute(delete(SaleAttrValue).where(SaleAttrValue.spu_id == spu_id))
    db.execute(delete(SpuSaleAttr).where(SpuSaleAttr.spu_id == spu_id))
    db.execute(delete(SpuImage).where(SpuImage.spu_id == spu_id))


def _insert_spu_children(
    db: Session,
    spu_id: int,
    images: list[tuple[str, str]],
    sale_attrs: list[tuple[int, str, list[str]]],
) -> None:
    """
    插入 SPU 的三张子表数据，供新增与整体覆盖复用
    :param images: [(image_name, image_url), ...]
    :param sale_attrs: [(base_sale_attr_id, sale_attr_name, [value_name, ...]), ...]
    """
    for image_name, image_url in images:
        db.add(
            SpuImage(
                image_id=snowflake.next_id(),
                image_name=image_name,
                image_url=image_url,
                spu_id=spu_id,
            )
        )
    for base_sale_attr_id, sale_attr_name, value_names in sale_attrs:
        db.add(
            SpuSaleAttr(
                spu_sale_attr_id=snowflake.next_id(),
                base_sale_attr_id=base_sale_attr_id,
                sale_attr_name=sale_attr_name,
                spu_id=spu_id,
            )
        )
        for value_name in value_names:
            db.add(
                SaleAttrValue(
                    sale_attr_value_id=snowflake.next_id(),
                    sale_attr_value_name=value_name,
                    sale_attr_id=base_sale_attr_id,
                    spu_id=spu_id,
                )
            )


def create_spu(
    db: Session,
    spu_name: str,
    description: str,
    category3_id: int,
    tm_id: int,
    images: list[tuple[str, str]],
    sale_attrs: list[tuple[int, str, list[str]]],
) -> Spu:
    """新增 SPU 及其全部子表数据：四表同一事务一次提交"""
    spu = Spu(
        spu_id=snowflake.next_id(),
        spu_name=spu_name,
        description=description,
        category3_id=category3_id,
        tm_id=tm_id,
    )
    db.add(spu)
    _insert_spu_children(db, spu.spu_id, images, sale_attrs)
    db.commit()
    return spu


def replace_spu(
    db: Session,
    target: Spu,
    spu_name: str,
    description: str,
    category3_id: int,
    tm_id: int,
    images: list[tuple[str, str]],
    sale_attrs: list[tuple[int, str, list[str]]],
) -> None:
    """整体覆盖 SPU：主表字段更新 + 三张子表先删后插（契约 12.3 原文）"""
    target.spu_name = spu_name
    target.description = description
    target.category3_id = category3_id
    target.tm_id = tm_id
    _delete_spu_children(db, target.spu_id)
    _insert_spu_children(db, target.spu_id, images, sale_attrs)
    db.commit()


def delete_spu(db: Session, spu_id: int) -> None:
    """
    删除 SPU：级联清三张子表后删本体（同一事务）
    sku 系五表为快照 + 销售数据，不级联（品牌删除同构决策）
    """
    _delete_spu_children(db, spu_id)
    db.execute(delete(Spu).where(Spu.spu_id == spu_id))
    db.commit()