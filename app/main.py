"""
FastAPI 应用入口
创建应用实例，注册路由和启动事件
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.database import engine
from app.models.base import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时：开发模式下自动创建表（生产环境请使用 Alembic 迁移）
    if settings.DEBUG:
        try:
            Base.metadata.create_all(bind=engine)
            print("[启动] 数据库表同步完成")
        except Exception as e:
            print(f"[启动] 数据库连接失败，跳过建表: {e}")
            print("[启动] 请检查 .env 中的 DATABASE_URL 是否正确，并确保 MySQL 已启动")
    yield
    # 关闭时：清理资源（如有需要）


app = FastAPI(
    title=settings.APP_NAME,
    description="硅谷甄选商城管理系统 API",
    version="0.1.0",
    lifespan=lifespan,
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
