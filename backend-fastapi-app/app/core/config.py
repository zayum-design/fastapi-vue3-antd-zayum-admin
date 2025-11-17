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
    
    ARROW_ROUTES: List[str] = []
    BABEL_DEFAULT_LOCALE: str = "ch"  # 默认值 'en'
    BABEL_DOMAIN: str = "messages"
    TIMEZONE: str = "UTC"

    # MySQL 配置
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_DB: str
    MYSQL_HOST: str
    MYSQL_PORT: int

    GENERATOR_ENABLED: bool = False

    # ----------------------------------------
    # 上传相关配置
    # ----------------------------------------
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 默认 10MB
    ALLOWED_EXTENSIONS: List[str] = ["jpg", "png", "gif", "txt", "pdf"]
    UPLOAD_DIR: str = "./uploads"
    PLUGINS_DIR: str = "./plugins"

    # ----------------------------------------
    # CORS 配置
    # ----------------------------------------
    ALLOW_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173", "http://demo.zayumadmin.com", "http://zayumadmin.com"]
    ALLOW_CREDENTIALS: bool = True
    ALLOW_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
    ALLOW_HEADERS: List[str] = ["*", "X-Captcha-Id"]
    EXPOSE_HEADERS: List[str] = ["X-Captcha-Id"]

    # ----------------------------------------
    # 缓存配置
    # ----------------------------------------
    CACHE_TYPE: str = "simple"  # "simple" 或 "redis"
    REDIS_URL: RedisURL = "redis://localhost:6379/0"
    
    # ----------------------------------------
    # Swagger UI 配置
    # ----------------------------------------
    SWAGGER_CSS_URL: str = "https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.9.0/swagger-ui.css"
    SWAGGER_FAVICON_URL: str = "https://fastapi.tiangolo.com/img/favicon.png"
    SWAGGER_BUNDLE_JS_URLS: List[str] = [
        "https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.9.0/swagger-ui-bundle.js",
        "https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-bundle.js"
    ]
    SWAGGER_PRESET_JS_URLS: List[str] = [
        "https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.9.0/swagger-ui-standalone-preset.js",
        "https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-standalone-preset.js"
    ]
    SWAGGER_LOADING_TEXT: str = "正在加载 API 文档..."
    SWAGGER_ERROR_MESSAGE: str = "无法加载 API 文档资源。请检查网络连接或使用 OpenAPI JSON 文件"

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
