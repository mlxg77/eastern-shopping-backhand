"""
用户模块 Schema
定义用户相关接口的请求体结构
"""

from pydantic import BaseModel, Field
from app.schemas.base import CamelModel

class LoginRequest(BaseModel):
    """登录请求体"""

    username: str
    password: str

class UserSaveRequest(BaseModel):
    """新增用户请求体"""

    username: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=64)


class UserUpdateRequest(BaseModel):
    """更新用户请求体"""

    id: int
    username: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=64)

class DoAssignRoleRequest(BaseModel):
    """为用户分配角色请求体（全量覆盖语义）"""

    userId: int
    roleIdList: list[int]

class UserInfoVO(CamelModel):
    """登录用户信息响应 VO（API.md 4.1：routes/buttons/roles/name/avatar）"""

    routes: list[str]
    buttons: list[str]
    roles: list[str]
    name: str
    avatar: str | None