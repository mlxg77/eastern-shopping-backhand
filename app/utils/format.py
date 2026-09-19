"""
格式化工具模块
实体字段到契约格式的转换
"""

from datetime import datetime


def fmt_time(dt: datetime | None) -> str:
    """时间格式化为 yyyy-MM-dd HH:mm:ss（API.md 2.4 约定）"""
    return dt.strftime("%Y-%m-%d %H:%M:%S") if dt else ""