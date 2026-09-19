"""
角色模型模块
映射数据库 role、user_role、role_menu 三张表
"""

from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Role(Base):
    """角色模型"""

    __tablename__ = "role"

    role_id: Mapped[int] = mapped_column(BigInteger, comment="业务角色ID")
    role_name: Mapped[str] = mapped_column(String(255), comment="角色名称")
    remark: Mapped[str | None] = mapped_column(String(255), comment="备注")


class UserRole(Base):
    """用户-角色关联模型（多对多中间表）"""

    __tablename__ = "user_role"

    user_id: Mapped[int] = mapped_column(BigInteger, comment="业务用户ID")
    role_id: Mapped[int] = mapped_column(BigInteger, comment="业务角色ID")


class RoleMenu(Base):
    """角色-菜单关联模型（多对多中间表）"""

    __tablename__ = "role_menu"

    role_id: Mapped[int] = mapped_column(BigInteger, comment="业务角色ID")
    menu_id: Mapped[int] = mapped_column(BigInteger, comment="业务菜单ID")