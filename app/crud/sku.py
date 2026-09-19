"""
SKU 数据访问模块
封装 sku 及其三张快照子表（平台属性 / 销售属性值 / 图片）的读写操作，
以及 13.1 / 13.2 对 spu 系表的只读查询
"""

from sqlalchemy import delete, func, select, update
from sqlalchemy.orm import Session

from app.models.sku import Sku, SkuAttrValue, SkuImage, SkuSaleAttrValue
from app.models.spu import SaleAttrValue, SpuImage, SpuSaleAttr
from app.utils.snowflake import snowflake


def get_spu_images(db: Session, spu_id: int) -> list[SpuImage]:
    """按 SPU 业务 ID 查询其全部图片（13.1）"""
    return list(
        db.execute(
            select(SpuImage)
            .where(SpuImage.spu_id == spu_id)
            .order_by(SpuImage.image_id)
        )
        .scalars()
        .all()
    )


def get_spu_sale_attrs_with_values(
    db: Session, spu_id: int
) -> list[tuple[SpuSaleAttr, list[SaleAttrValue]]]:
    """
    按 SPU 业务 ID 查询销售属性及其值的双层结构（13.2）
    对齐键：sale_attr_value.sale_attr_id == spu_sale_attr.base_sale_attr_id
    （兄弟表非父子，第 12 章勘察 8/8）；分组模式：一次查全表 + 字典索引
    """
    attrs = list(
        db.execute(
            select(SpuSaleAttr)
            .where(SpuSaleAttr.spu_id == spu_id)
            .order_by(SpuSaleAttr.spu_sale_attr_id)
        )
        .scalars()
        .all()
    )
    values = list(
        db.execute(
            select(SaleAttrValue).where(SaleAttrValue.spu_id == spu_id)
        )
        .scalars()
        .all()
    )
    grouped: dict[int, list[SaleAttrValue]] = {}
    for v in values:
        grouped.setdefault(v.sale_attr_id, []).append(v)
    return [(a, grouped.get(a.base_sale_attr_id, [])) for a in attrs]


def create_sku(
    db: Session,
    *,
    spu_id: int,
    category3_id: int,
    tm_id: int,
    sku_name: str,
    price: int,
    weight: str,
    sku_desc: str,
    sku_default_img: str,
    is_sale: int,
    attr_values: list[tuple[int, int, str, str]],
    sale_attr_values: list[tuple[int, int, str, str]],
    images: list[tuple[str, int, str]],
) -> Sku:
    """
    新增 SKU 及其三张快照子表：四表同一事务一次提交（与 12.2 四表同插同构）
    :param attr_values: [(attr_id, value_id, value_name, attr_name), ...]
    :param sale_attr_values: [(sale_attr_id, sale_attr_value_id, sale_attr_name, sale_attr_value_name), ...]
    :param images: [(image_url, spu_image_id, is_default), ...]
    参数 12 个，全部 keyword-only：这个规模的位置传参一个错位就是静默数据错乱
    """
    sku = Sku(
        sku_id=snowflake.next_id(),
        spu_id=spu_id,
        category_3_id=category3_id,
        tm_id=tm_id,
        sku_name=sku_name,
        weight=weight,
        price=price,
        sku_desc=sku_desc,
        sku_default_img=sku_default_img,
        is_sale=is_sale,
    )
    db.add(sku)
    for attr_id, value_id, value_name, attr_name in attr_values:
        db.add(
            SkuAttrValue(
                sku_attr_value_id=snowflake.next_id(),
                attr_id=attr_id,
                value_id=value_id,
                value_name=value_name,
                attr_name=attr_name,
                sku_id=sku.sku_id,
            )
        )
    for (
        sale_attr_id,
        sale_attr_value_id,
        sale_attr_name,
        sale_attr_value_name,
    ) in sale_attr_values:
        db.add(
            SkuSaleAttrValue(
                sku_sale_attr_value_id=snowflake.next_id(),
                sale_attr_id=sale_attr_id,
                sale_attr_value_id=sale_attr_value_id,
                sale_attr_name=sale_attr_name,
                sale_attr_value_name=sale_attr_value_name,
                sku_id=sku.sku_id,
            )
        )
    for image_url, spu_image_id, is_default in images:
        db.add(
            SkuImage(
                image_id=snowflake.next_id(),
                sku_id=sku.sku_id,
                image_url=image_url,
                spu_image_id=spu_image_id,
                is_default=is_default,
            )
        )
    db.commit()
    return sku


def get_skus_by_spu_id(db: Session, spu_id: int) -> list[Sku]:
    """按 SPU 业务 ID 查询其全部 SKU（13.4）"""
    return list(
        db.execute(
            select(Sku).where(Sku.spu_id == spu_id).order_by(Sku.sku_id)
        )
        .scalars()
        .all()
    )


def get_sku_page(
    db: Session, page: int, limit: int, spu_id: int | None = None
) -> tuple[list[Sku], int]:
    """分页查询 SKU（13.5）：spu_id 传入时按所属 SPU 过滤"""
    count_stmt = select(func.count()).select_from(Sku)
    list_stmt = select(Sku).order_by(Sku.sku_id)
    if spu_id is not None:
        count_stmt = count_stmt.where(Sku.spu_id == spu_id)
        list_stmt = list_stmt.where(Sku.spu_id == spu_id)
    total = db.execute(count_stmt).scalar_one()
    skus = list(
        db.execute(list_stmt.offset((page - 1) * limit).limit(limit))
        .scalars()
        .all()
    )
    return skus, total


def get_sku_by_sku_id(db: Session, sku_id: int) -> Sku | None:
    """按业务 ID 查询 SKU（sku_id 无唯一索引，limit(1) 保证多行不炸）"""
    return db.execute(
        select(Sku).where(Sku.sku_id == sku_id).limit(1)
    ).scalars().first()


def get_sku_children(
    db: Session, sku_ids: list[int]
) -> tuple[
    dict[int, list[SkuAttrValue]],
    dict[int, list[SkuSaleAttrValue]],
    dict[int, list[SkuImage]],
]:
    """
    批量查询多个 SKU 的三张快照子表，按 sku_id 分组（13.4 / 13.6 嵌套装配）
    三次 IN 查询代替逐 SKU 查询，避免 N+1
    """
    if not sku_ids:
        return {}, {}, {}
    attr_map: dict[int, list[SkuAttrValue]] = {}
    for v in (
        db.execute(
            select(SkuAttrValue)
            .where(SkuAttrValue.sku_id.in_(sku_ids))
            .order_by(SkuAttrValue.sku_attr_value_id)
        )
        .scalars()
    ):
        attr_map.setdefault(v.sku_id, []).append(v)
    sale_map: dict[int, list[SkuSaleAttrValue]] = {}
    for v in (
        db.execute(
            select(SkuSaleAttrValue)
            .where(SkuSaleAttrValue.sku_id.in_(sku_ids))
            .order_by(SkuSaleAttrValue.sku_sale_attr_value_id)
        )
        .scalars()
    ):
        sale_map.setdefault(v.sku_id, []).append(v)
    image_map: dict[int, list[SkuImage]] = {}
    for i in (
        db.execute(
            select(SkuImage)
            .where(SkuImage.sku_id.in_(sku_ids))
            .order_by(SkuImage.image_id)
        )
        .scalars()
    ):
        image_map.setdefault(i.sku_id, []).append(i)
    return attr_map, sale_map, image_map


def set_sku_sale(db: Session, sku_id: int, is_sale: int) -> None:
    """更新 SKU 上下架状态（13.7）：不存在的 sku_id 影响 0 行，天然幂等"""
    db.execute(update(Sku).where(Sku.sku_id == sku_id).values(is_sale=is_sale))
    db.commit()


def delete_sku(db: Session, sku_id: int) -> None:
    """
    删除 SKU（13.8）：级联清三张快照子表后删本体（同一事务）
    对照第 12 章：删 SPU 不动 sku 系（那是销售数据，订单还在引用）；
    删 SKU 清快照（快照行属于 SKU 自己，主体没了就是无主孤儿）
    """
    db.execute(delete(SkuAttrValue).where(SkuAttrValue.sku_id == sku_id))
    db.execute(delete(SkuSaleAttrValue).where(SkuSaleAttrValue.sku_id == sku_id))
    db.execute(delete(SkuImage).where(SkuImage.sku_id == sku_id))
    db.execute(delete(Sku).where(Sku.sku_id == sku_id))
    db.commit()