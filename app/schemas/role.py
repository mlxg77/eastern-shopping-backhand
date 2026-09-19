"""
角色模块 Schema
定义角色相关接口的请求体结构，以及 Role 实体的序列化
"""

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.role import Role

class RoleSaveRequest(BaseModel):
    """新增角色请求体"""

    roleName: str = Field(min_length=1, max_length=255)
    remark: str | None = Field(default=None, max_length=255)


class RoleUpdateRequest(BaseModel):
    """更新角色请求体（全量覆盖语义）"""

    id: int
    roleName: str = Field(min_length=1, max_length=255)
    remark: str | None = Field(default=None, max_length=255)

def _fmt_time(dt: datetime | None) -> str:
    """时间格式化为 yyyy-MM-dd HH:mm:ss（API.md 2.4 约定）"""
    return dt.strftime("%Y-%m-%d %H:%M:%S") if dt else ""


def role_to_dict(role: Role) -> dict:
    """Role 实体 -> 契约 Role 结构（id/roleName/remark/createTime）"""
    return {
        "id": role.role_id,
        "roleName": role.role_name,
        "remark": role.remark or "",
        "createTime": _fmt_time(role.create_time),
    }