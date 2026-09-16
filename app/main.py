"""
FastAPI 应用入口
创建应用实例，注册路由和启动事件
"""

import logging

from fastapi import FastAPI

from app.config import settings
from app.logging_config import setup_logging

setup_logging()

logger = logging.getLogger(__name__)


app = FastAPI(
    title=settings.APP_NAME,
    description="硅谷甄选商城管理系统 API",
    version="0.1.0",
)


# ============================================================
# 健康检查
# ============================================================

@app.get("/", tags=["健康检查"])
def root():
    """健康检查接口"""
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": "0.1.0",
    }


# ============================================================
# 路由注册（后续添加业务模块时在此处 include_router）
# ============================================================
# 示例：
# from app.api import products
# app.include_router(products.router, prefix="/api/products", tags=["商品管理"])
