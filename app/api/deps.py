"""
公共依赖模块
提供路由中常用的依赖注入函数
"""

from typing import Generator

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.crud import user as user_crud
from app.database import SessionLocal
from app.exceptions import BizCode, BizException
from app.models.user import User
from app.utils.jwt_utils import parse_token


def get_db() -> Generator[Session, None, None]:
    """
    数据库 session 依赖
    在路由函数中通过 Depends(get_db) 注入
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: str | None = Header(default=None, alias="Token", description="登录后获取的 Token"),
    db: Session = Depends(get_db),
) -> User:
    """
    当前登录用户依赖：解析请求头中的 Token 并返回对应用户
    :return: 当前登录的 User 对象
    :raises BizException: 未携带 Token → 207；Token 无效/过期/用户不存在 → 206
    """
    # 1. 未携带 Token → 207 未登录（前端据此跳登录页）
    if not token:
        raise BizException(BizCode.NEED_LOGIN)

    # 2. 解析 Token（签名、过期校验在 parse_token 内部完成，失败抛 206）
    payload = parse_token(token)

    # 3. 按业务 ID 查用户：防止 Token 本身有效、但用户已经被删的情况
    user = user_crud.get_user_by_user_id(db, payload["user_id"])
    if user is None:
        raise BizException(BizCode.INVALID_TOKEN)

    return user