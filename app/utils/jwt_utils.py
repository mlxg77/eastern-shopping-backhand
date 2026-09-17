"""
JWT 工具模块
负责 Token 的签发与解析
"""

from datetime import datetime, timedelta, timezone

import jwt

from app.config import settings
from app.exceptions import BizCode, BizException


def create_token(user_id: int) -> str:
    """
    签发 Token
    :param user_id: 用户的业务 ID（雪花 ID），放在载荷中供后续接口识别身份
    :return: JWT 字符串
    """
    payload = {
        "user_id": user_id,
        # 过期时间：必须用「带时区的 UTC 时间」
        "exp": datetime.now(timezone.utc)
        + timedelta(minutes=settings.JWT_EXPIRE_MINUTES),
    }
    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def parse_token(token: str) -> dict:
    """
    解析并校验 Token（自动校验签名与过期时间）
    :param token: JWT 字符串
    :return: 载荷字典
    :raises BizException: 无效或已过期 → 206 无效的 Token
    """
    try:
        return jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except jwt.PyJWTError:
        raise BizException(BizCode.INVALID_TOKEN)