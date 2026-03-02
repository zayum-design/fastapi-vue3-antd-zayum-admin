"""
应用配置管理
支持多环境配置（开发/测试/生产）
"""

import os
from enum import Enum
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Environment(str, Enum):
    """环境类型枚举"""

    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class BaseConfig(BaseSettings):
    """
    基础配置类
    包含所有环境通用的配置项
    """

    # 项目信息
    PROJECT_NAME: str = "Zayum Admin"
    API_ADMIN_STR: str = "/api/v1"
    VERSION: str = "1.0.0"

    # 安全配置
    SECRET_KEY: str = Field(default="your_secret_key_here", description="JWT 密钥")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7天

    # Redis 配置
    REDIS_URL: str = "redis://localhost:6379/0"

    # 国际化配置
    ARROW_ROUTES: list[str] = []
    BABEL_DEFAULT_LOCALE: str = "ch"
    BABEL_DOMAIN: str = "messages"
    TIMEZONE: str = "UTC"

    # MySQL 配置（不提供默认值，强制从环境变量读取）
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_DB: str
    MYSQL_HOST: str
    MYSQL_PORT: int

    # 上传配置
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: list[str] = ["jpg", "png", "gif", "txt", "pdf"]
    UPLOAD_DIR: str = "./uploads"
    PLUGINS_DIR: str = "./plugins"

    # CORS 配置
    ALLOW_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    ALLOW_CREDENTIALS: bool = True
    ALLOW_METHODS: list[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
    ALLOW_HEADERS: list[str] = ["*", "X-Captcha-Id"]
    EXPOSE_HEADERS: list[str] = ["X-Captcha-Id"]

    # 缓存配置
    CACHE_TYPE: str = "simple"  # "simple" 或 "redis"

    # Swagger UI 配置
    SWAGGER_CSS_URL: str = "https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.9.0/swagger-ui.css"
    SWAGGER_FAVICON_URL: str = "https://fastapi.tiangolo.com/img/favicon.png"
    SWAGGER_BUNDLE_JS_URLS: list[str] = [
        "https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.9.0/swagger-ui-bundle.js",
        "https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
    ]
    SWAGGER_PRESET_JS_URLS: list[str] = [
        "https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.9.0/swagger-ui-standalone-preset.js",
        "https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-standalone-preset.js",
    ]
    SWAGGER_LOADING_TEXT: str = "正在加载 API 文档..."
    SWAGGER_ERROR_MESSAGE: str = "无法加载 API 文档资源。请检查网络连接或使用 OpenAPI JSON 文件"

    # 功能开关
    GENERATOR_ENABLED: bool = False

    # 环境
    ENV: Environment = Environment.DEVELOPMENT
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    TESTING: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "forbid"
        use_enum_values = True

    @field_validator("VERSION", mode="before")
    @classmethod
    def load_version_from_file(cls, v):
        """从 VERSION 文件加载版本号"""
        if v and v != "1.0.0":
            return v
        try:
            version_file = Path(__file__).parent.parent.parent.parent.parent / "VERSION"
            if version_file.exists():
                version = version_file.read_text().strip()
                return version if version else "unknown"
        except Exception:
            pass
        return "unknown"

    @property
    def DATABASE_URL(self) -> str:
        """生成数据库连接字符串"""
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}"

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        """生成异步数据库连接字符串"""
        return f"mysql+asyncmy://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}"


class DevelopmentConfig(BaseConfig):
    """开发环境配置"""

    ENV: Environment = Environment.DEVELOPMENT
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"

    # 开发环境放宽 CORS
    ALLOW_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://localhost:8080",
        "*",
    ]

    # 开发环境使用 .env 文件（继承基类配置）
    class Config(BaseConfig.Config):
        pass


class TestingConfig(BaseConfig):
    """测试环境配置"""

    ENV: Environment = Environment.TESTING
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    TESTING: bool = True

    # 测试环境使用 .env.testing 文件
    class Config(BaseConfig.Config):
        env_file = ".env.testing"


class ProductionConfig(BaseConfig):
    """生产环境配置"""

    ENV: Environment = Environment.PRODUCTION
    DEBUG: bool = False
    LOG_LEVEL: str = "WARNING"

    # 生产环境严格的 CORS
    ALLOW_ORIGINS: list[str] = ["https://admin.zayum.com", "https://zayumadmin.com"]

    # 生产环境更大的文件限制
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB

    # 生产环境使用 Redis 缓存
    CACHE_TYPE: str = "redis"

    # 生产环境使用 .env.production 文件
    class Config(BaseConfig.Config):
        env_file = ".env.production"


# 配置映射
_CONFIG_MAP = {
    Environment.DEVELOPMENT: DevelopmentConfig,
    Environment.TESTING: TestingConfig,
    Environment.PRODUCTION: ProductionConfig,
}


def get_settings() -> BaseConfig:
    """
    根据环境变量获取对应的配置实例

    Returns:
        BaseConfig: 配置实例
    """
    env_str = os.getenv("ENV", "development").lower()

    # 将字符串转换为枚举
    try:
        env = Environment(env_str)
    except ValueError:
        env = Environment.DEVELOPMENT

    config_class = _CONFIG_MAP.get(env, DevelopmentConfig)
    return config_class()


# 全局配置实例
settings = get_settings()


def reload_settings() -> BaseConfig:
    """
    重新加载配置
    用于配置热更新场景

    Returns:
        BaseConfig: 新的配置实例
    """
    global settings
    settings = get_settings()
    return settings
