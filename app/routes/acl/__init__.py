"""
ACL 权限模块路由
聚合本模块所有子路由，main.py 只需注册这里导出的 router
"""

from fastapi import APIRouter

from app.routes.acl.index import router as index_router
from app.routes.acl.user import router as user_router
from app.routes.acl.role import router as role_router
from app.routes.acl.permission import router as permission_router


router = APIRouter()
router.include_router(index_router)
router.include_router(user_router)
router.include_router(permission_router)
router.include_router(role_router)