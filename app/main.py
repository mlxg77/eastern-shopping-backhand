"""
FastAPI 应用入口
创建应用实例，注册路由和启动事件
"""

import logging

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.exception_handlers import register_exception_handlers
from app.config import settings, setup_logging
from app.routes.acl import router as acl_router
from app.routes.product import router as product_router

from app.utils.response import success
from fastapi.middleware.cors import CORSMiddleware

setup_logging()

logger = logging.getLogger(__name__)


app = FastAPI(
    title=settings.APP_NAME,
    description="硅谷甄选商城管理系统 API",
    version="0.1.0",
)
# ============================================================
# 跨域设置
# ============================================================ 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite 默认端口，即前端的来源
    allow_methods=["*"],
    allow_headers=["*"],  # 关键：放行自定义的 token 请求头
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

app.include_router(acl_router)
app.include_router(product_router)


# ============================================================
# 静态资源服务：上传文件的访问入口
# ============================================================

# 上传目录自举：StaticFiles 不接受不存在的目录，启动时确保 static/ 存在
Path("static").mkdir(exist_ok=True)
# 规则：剥掉 /static 前缀 → 按剩余相对路径在磁盘 static/ 目录里实时查文件
app.mount("/static", StaticFiles(directory="static"), name="static")