"""
配置管理模块
使用 pydantic-settings 从 .env 文件读取配置
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""

    APP_NAME: str = "硅谷甄选商城管理系统"
    DEBUG: bool = False

    # 数据库连接字符串
    # 格式: mysql+pymysql://用户名:密码@主机:端口/数据库名?charset=utf8mb4
    DATABASE_URL: str = "mysql+pymysql://root:your_password@localhost:3306/guigu_shopping?charset=utf8mb4"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


# 全局配置单例
settings = Settings()
