"""
product 模块路由
聚合本模块所有子路由，main.py 只需注册这里导出的 router

⚠️ include_router 顺序是匹配语义依赖，不是风格约定：
spu 的 GET /{page}/{limit} 是域根级两段通配，会吞噬一切晚于它注册的
两段 GET——category（getCategory2/getCategory3）、sku（spuImageList/
getSkuInfo 等）以及 trademark（getTrademarkList 完整路径恰为两段）
都必须注册在 spu 之前。
当前注册顺序：attr → category → file_upload → sku → trademark → spu
（import 区保持字母序，注册序独立表达匹配语义），重排前必须想清楚。
"""

from fastapi import APIRouter

from app.routes.product.attr import router as attr_router
from app.routes.product.category import router as category_router
from app.routes.product.file_upload import router as file_upload_router
from app.routes.product.sku import router as sku_router
from app.routes.product.spu import router as spu_router
from app.routes.product.trademark import router as trademark_router

router = APIRouter()

router.include_router(attr_router)
router.include_router(category_router)
router.include_router(file_upload_router)
router.include_router(sku_router)
router.include_router(trademark_router)
router.include_router(spu_router)