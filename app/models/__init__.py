"""
模型包
统一导出所有模型，供 Alembic 自动发现
"""

from app.models.base import Base
from app.models.menu import Menu
from app.models.role import Role, RoleMenu, UserRole
from app.models.user import User

__all__ = ["Base", "Menu", "Role", "RoleMenu", "User", "UserRole"]