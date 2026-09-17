"""
模型包
统一导出所有模型，供 Alembic 自动发现
"""

from app.models.base import Base
from app.models.user import User

# 
__all__ = ["Base", "User"]