# app/core/config.py
from pydantic_settings import BaseSettings
from pydantic import Field, AnyUrl
from typing import List


class RedisURL(AnyUrl):
    allowed_schemes = {"redis"}


class Settings(BaseSettings):
    # ----------------------------------------
    # 以下是你已有的项目基础配置
    # ----------------------------------------
    PROJECT_NAME: str = "Zayum Admin"
    API_ADMIN_STR: str = "/api/v1"
    SECRET_KEY: str = "your_secret_key_here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7天
    
    REDIS_URL: RedisURL = "redis://localhost:6379/0"
    
    ARROW_ROUTES: List[str] = Field(default=[], env="ARROW_ROUTES")
    BABEL_DEFAULT_LOCALE: str = "ch"  # 默认值 'en'
    BABEL_DOMAIN: str = "messages"
    TIMEZONE: str = Field("UTC", env="TIMEZONE")

    # MySQL 配置
    MYSQL_USER: str = Field(..., env="MYSQL_USER")
    MYSQL_PASSWORD: str = Field(..., env="MYSQL_PASSWORD")
    MYSQL_DB: str = Field(..., env="MYSQL_DB")
    MYSQL_HOST: str = Field(..., env="MYSQL_HOST")
    MYSQL_PORT: int = Field(..., env="MYSQL_PORT")

    GENERATOR_ENABLED: bool = Field(False, env="GENERATOR_ENABLED")

    # ----------------------------------------
    # 上传相关配置
    # ----------------------------------------
    MAX_FILE_SIZE: int = Field(
        10 * 1024 * 1024,  # 默认 10MB
        env="MAX_FILE_SIZE",
        description="文件上传的最大大小（字节）"
    )
    ALLOWED_EXTENSIONS: List[str] = Field(
        default=["jpg", "png", "gif", "txt", "pdf"],
        env="ALLOWED_EXTENSIONS",
        description="允许的文件扩展名"
    )
    UPLOAD_DIR: str = Field(
        "./uploads",
        env="UPLOAD_DIR",
        description="文件上传的存储目录"
    )
    
    PLUGINS_DIR: str = Field(
        "./plugins",
        env="PLUGINS_DIR",
        description="插件目录"
    )

    # 计算属性，用于生成数据库连接字符串
    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "forbid"  # 禁止额外的字段


# 实例化设置
settings = Settings()
