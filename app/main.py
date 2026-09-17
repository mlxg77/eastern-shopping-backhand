"""
FastAPI 应用入口
创建应用实例，注册路由和启动事件
"""

import logging

from fastapi import FastAPI

from app.api.exception_handlers import register_exception_handlers
from app.routes.acl.index import router as acl_index_router
from app.config import settings, setup_logging
from app.utils.response import success

setup_logging()

logger = logging.getLogger(__name__)


app = FastAPI(
    title=settings.APP_NAME,
    description="硅谷甄选商城管理系统 API",
    version="0.1.0",
)

# 注册全局异常处理器：保证所有错误也按统一格式返回
register_exception_handlers(app)

# ============================================================
# 健康检查
# ============================================================

@app.get("/", tags=["健康检查"])
def root():
    """健康检查接口"""
    return success({
        "status": "ok",
        "app": settings.APP_NAME,
        "version": "0.1.0",
    })

# ============================================================
# 路由注册
# ============================================================

app.include_router(acl_index_router)