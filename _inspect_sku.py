"""第13章开工前事实核对：sku_image + sku 系表结构与值域（临时脚本，跑完即删）"""
import sys

sys.stdout.reconfigure(encoding="utf-8")

from sqlalchemy import text

from app.database import engine

with engine.connect() as conn:
    for t in ["sku_image", "sku", "sku_attr_value", "sku_sale_attr_value"]:
        print(f"\n===== {t} =====")
        for r in conn.execute(text(f"SHOW COLUMNS FROM `{t}`")):
            print("  ", tuple(r))
        n = conn.execute(text(f"SELECT COUNT(*) FROM `{t}`")).scalar_one()
        print("  行数:", n)
        for r in conn.execute(text(f"SELECT * FROM `{t}` LIMIT 3")):
            print("  ", tuple(r))

    # sku_image 引用链：sku_id 与 spu 图?
    print("\n===== 引用链 =====")
    for r in conn.execute(text(
        "SELECT COUNT(*) FROM sku_image i JOIN sku s ON i.sku_id = s.sku_id")):
        print("  sku_image.sku_id ↔ sku.sku_id:", tuple(r))
    for r in conn.execute(text(
        "SELECT COUNT(*) FROM sku_image i JOIN sku s ON i.sku_id = s.id")):
        print("  sku_image.sku_id ↔ sku.id(物理):", tuple(r))

    # is_default 值域（契约 isDefault "1"/"0" 字符串）
    print("\n===== sku_image.is_default 值域 =====")
    for r in conn.execute(text("SELECT DISTINCT is_default FROM sku_image")):
        print("  ", tuple(r))

    # sku.weight 存量形态（DB varchar）
    print("\n===== sku.weight 存量 =====")
    for r in conn.execute(text("SELECT weight, price, is_sale FROM sku")):
        print("  ", tuple(r))

    # 13.4/13.5 验收靶场：sku.spu_id 分布
    print("\n===== sku 按 spu_id 分布 =====")
    for r in conn.execute(text("SELECT spu_id, COUNT(*) FROM sku GROUP BY spu_id")):
        print("  ", tuple(r))

    # 13.2 验收靶场：spu_sale_attr + sale_attr_value 对齐形态（拿 oppo 那个 SPU 看看）
    print("\n===== 9304018587776 SPU 的图片与销售属性 =====")
    for r in conn.execute(text("SELECT image_id, image_name, spu_id FROM spu_image_list WHERE spu_id = 9304018587776")):
        print("  img:", tuple(r))
    for r in conn.execute(text("SELECT spu_sale_attr_id, base_sale_attr_id, sale_attr_name, spu_id FROM spu_sale_attr WHERE spu_id = 9304018587776")):
        print("  attr:", tuple(r))
    for r in conn.execute(text("SELECT sale_attr_value_id, sale_attr_value_name, sale_attr_id, spu_id FROM sale_attr_value WHERE spu_id = 9304018587776")):
        print("  val:", tuple(r))
