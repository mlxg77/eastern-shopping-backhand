"""
统一响应封装模块
按接口文档 2.2 的格式构造响应体
"""

from fastapi.responses import JSONResponse


def success(data=None, message: str = "success") -> dict:
    """
    成功响应体（路由直接 return，FastAPI 会自动序列化为 JSON）
    :param data: 业务数据，无数据时传 None
    :param message: 提示信息
    """
    return {
        "code": 200,
        "message": message,
        "data": data,
        "ok": True,
    }


def fail(code: int, message: str) -> JSONResponse:
    """
    错误响应（供全局异常处理器直接返回）
    注意：异常处理器必须返回 Response 对象，不能像普通路由那样返回 dict
    :param code: 业务状态码
    :param message: 错误提示
    """
    return JSONResponse(
        status_code=200,
        content={
            "code": code,
            "message": message,
            "data": None,
            "ok": False,
        },
    )

def page_result(records: list, total: int, page: int, limit: int) -> dict:
    """
    统一分页结构（API.md 2.4）：records/total/size/current/pages
    :param records: 当前页记录列表（驼峰化、序列化完成的字典列表）
    """
    return {
        "records": records,
        "total": total,
        "size": limit,
        "current": page,
        "pages": (total + limit - 1) // limit,
    }