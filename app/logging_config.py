"""
日志配置模块
统一配置全项目的 logging 格式和输出
"""

import logging
import sys

from app.config import settings


def setup_logging() -> None:
    """初始化日志配置"""

    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    # 日志格式：时间 | 级别 | 模块名 | 内容
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 控制台输出
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    # 配置根 logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(handler)

    # 降低第三方库的日志级别，避免刷屏
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    # SQLAlchemy 的 echo 自带输出，禁止向上传播避免重复
    sa_logger = logging.getLogger("sqlalchemy.engine")
    sa_logger.propagate = False
    if settings.DEBUG:
        sa_handler = logging.StreamHandler(sys.stdout)
        sa_handler.setFormatter(formatter)
        sa_logger.addHandler(sa_handler)
        sa_logger.setLevel(logging.INFO)
