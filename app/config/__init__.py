"""
配置包
统一导出 settings 单例和日志初始化函数
"""

from app.config.settings import settings
from app.config.logging_config import setup_logging

__all__ = ["settings", "setup_logging"]
