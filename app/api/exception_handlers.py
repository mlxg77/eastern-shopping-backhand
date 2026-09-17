"""
全局异常处理器
把各类异常统一转换为「HTTP 200 + 业务状态码」的规范响应

对应接口文档 2.2：无论成功失败，HTTP 状态码均为 200
"""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.exceptions import BizCode, BizException
from app.utils.response import fail

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """把全局异常处理器注册到 FastAPI 应用上"""

    @app.exception_handler(BizException)
    async def biz_exception_handler(request: Request, exc: BizException):
        """业务异常：按抛出的业务码和提示原样返回"""
        return fail(exc.code, exc.message)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """请求参数校验失败（Pydantic 拦截）→ 201"""
        logger.warning(
            "参数校验失败: %s %s | %s", request.method, request.url.path, exc.errors()
        )
        return fail(BizCode.PARAM_ERROR, "请求参数错误")

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """路由不存在（404）/ 方法不允许（405）等 HTTP 异常 → 209"""
        message = "请求路径不存在" if exc.status_code == 404 else str(exc.detail)
        return fail(BizCode.PATH_NOT_FOUND, message)

    @app.exception_handler(Exception)
    async def unknown_exception_handler(request: Request, exc: Exception):
        """兜底：未预期的异常 → 205，堆栈只进日志、不给前端"""
        logger.exception("服务内部错误: %s %s", request.method, request.url.path)
        return fail(BizCode.SERVER_BUSY, "服务繁忙")