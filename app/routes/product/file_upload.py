"""
商品文件上传路由
对应接口文档第 8 章：文件上传
"""

import shutil
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, File, UploadFile

from app.api.deps import get_current_user
from app.exceptions import BizCode, BizException
from app.models.user import User
from app.utils.response import success
from app.utils.snowflake import snowflake

router = APIRouter(prefix="/admin/product", tags=["文件上传"])

# 上传归档根目录（相对项目根；uvicorn 须从项目根目录启动）
UPLOAD_DIR = Path("static/img/sph")


@router.post("/fileUpload")
def upload_file(
    file: UploadFile = File(..., description="图片文件"),
    user: User = Depends(get_current_user),
):
    """上传图片；按上传日期归档，返回契约形状的图片访问 URL"""
    # 1. 校验：契约定义上传的是图片文件（MIME 前缀判定）
    if not (file.content_type or "").startswith("image/"):
        raise BizException(BizCode.PARAM_ERROR, "只能上传图片文件")

    # 2. 文件名安全：只取原始文件名的 basename，防路径穿越（../.. 恶意路径）
    raw_name = Path(file.filename or "").name
    if not raw_name:
        raise BizException(BizCode.PARAM_ERROR, "文件名不能为空")

    # 3. 按日期归档 + 雪花前缀防同日同名覆盖
    date_dir = datetime.now().strftime("%Y%m%d")
    dest_dir = UPLOAD_DIR / date_dir
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"{snowflake.next_id()}-{raw_name}"

    # 4. 流式拷贝落盘（UploadFile.file 是 SpooledTemporaryFile）
    with dest.open("wb") as out:
        shutil.copyfileobj(file.file, out)

    # 5. 返回契约形状 URL：前端代理剥掉 /api 前缀后打到本服务的 /static
    # dest.name 是 pathlib.Path 对象的内置属性，取的是路径的最后一段——也就是纯文件名，不含任何目录部分。
    return success(f"/api/static/img/sph/{date_dir}/{dest.name}")