"""
日志配置
统一配置全项目的 logging 格式和输出
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.config.settings import settings

# 日志目录（容器部署时由 docker-compose 挂载到宿主机，日志长期留存）
LOG_DIR = Path("logs")


def setup_logging() -> None:
    """初始化日志配置"""

    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    # 日志格式：时间 | 级别 | 模块名 | 内容
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 控制台输出
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # 文件输出：按大小轮转（10MB 一档，保留 5 份历史）
    # 挂载到宿主机后，可直接在服务器上 tail -f logs/app.log 查看
    LOG_DIR.mkdir(exist_ok=True)
    file_handler = RotatingFileHandler(
        LOG_DIR / "app.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    # 配置根 logger：业务日志（app.* 等）同时进控制台和文件
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    # uvicorn 自身的启动/报错日志默认只进控制台，补一个文件 handler 让它也落盘
    for name in ("uvicorn", "uvicorn.error"):
        logging.getLogger(name).addHandler(file_handler)

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
