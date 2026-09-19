"""
product 模块路由
聚合本模块所有子路由，main.py 只需注册这里导出的 router
"""

from fastapi import APIRouter

from app.routes.product.file_upload import router as file_upload_router
from app.routes.product.trademark import router as trademark_router

router = APIRouter()

router.include_router(file_upload_router)
router.include_router(trademark_router)
