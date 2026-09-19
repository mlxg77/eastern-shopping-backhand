"""
品牌模块 Schema
定义品牌相关接口的请求体结构，以及 Trademark 实体的序列化
"""

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.trademark import Trademark


class TrademarkSaveRequest(BaseModel):
    """新增品牌请求体"""

    tmName: str = Field(min_length=1, max_length=255)
    logoUrl: str = Field(min_length=1, max_length=255)


class TrademarkUpdateRequest(BaseModel):
    """更新品牌请求体"""

    id: int
    tmName: str = Field(min_length=1, max_length=255)
    logoUrl: str = Field(min_length=1, max_length=255)


def _fmt_time(dt: datetime | None) -> str:
    """时间格式化为 yyyy-MM-dd HH:mm:ss（API.md 2.4 约定）"""
    return dt.strftime("%Y-%m-%d %H:%M:%S") if dt else ""


def trademark_to_dict(trademark: Trademark) -> dict:
    """Trademark 实体 -> 契约品牌结构（id/tmName/logoUrl/createTime）"""
    return {
        "id": trademark.tm_id,
        "tmName": trademark.tm_name,
        "logoUrl": trademark.logo_url,
        "createTime": _fmt_time(trademark.create_time),
    }