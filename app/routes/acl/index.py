"""
ACL 登录认证路由
对应接口文档第 3 章：用户登录 / 用户登出
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud import user as user_crud
from app.exceptions import BizCode, BizException
from app.schemas.user import LoginRequest
from app.utils.jwt_utils import create_token
from app.utils.response import success

router = APIRouter(prefix="/admin/acl/index", tags=["登录认证"])


@router.post("/login")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    """用户登录：校验用户名密码，签发 Token"""
    # 1. 按用户名查用户
    user = user_crud.get_user_by_username(db, body.username)
    if user is None:
        raise BizException(BizCode.USERNAME_NOT_FOUND)  # 203

    # 2. 校验密码（当前数据为明文存储，字符串直接比对）
    if user.password != body.password:
        raise BizException(BizCode.PASSWORD_ERROR)  # 204

    # 3. 签发 Token（载荷放业务 ID user_id）
    token = create_token(user.user_id)
    return success(token)


@router.post("/logout")
def logout():
    """用户登出：无状态实现，服务端不做处理，前端清除本地 Token 即可"""
    return success()