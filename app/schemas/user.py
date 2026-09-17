"""
用户模块 Schema
定义用户相关接口的请求体结构
"""

from pydantic import BaseModel


class LoginRequest(BaseModel):
    """登录请求体"""

    username: str
    password: str