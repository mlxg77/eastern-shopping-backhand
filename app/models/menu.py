"""
菜单模型模块
映射数据库 menu 表（菜单 + 按钮权限）
"""

from sqlalchemy import BigInteger, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Menu(Base):
    """菜单模型：type=1 菜单/路由，type=2 按钮"""

    __tablename__ = "menu"

    menu_id: Mapped[int] = mapped_column(BigInteger, comment="业务菜单ID")
    pid: Mapped[int] = mapped_column(BigInteger, comment="父级菜单ID（0 表示根）")
    name: Mapped[str] = mapped_column(String(100), comment="菜单名称")
    code: Mapped[str] = mapped_column(String(100), comment="权限 code")
    to_code: Mapped[str] = mapped_column(String(100), comment="跳转目标 code")
    type: Mapped[int] = mapped_column(Integer, comment="类型：1 菜单，2 按钮")
    status: Mapped[str] = mapped_column(String(100), comment="状态（存量数据全为空串）")
    level: Mapped[int] = mapped_column(Integer, comment="菜单层级")