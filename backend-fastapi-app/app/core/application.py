"""
FastAPI 应用创建和配置模块
"""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_babel import BabelConfigs, BabelMiddleware

from app.core import handlers
from app.core.config import settings
from app.core.middleware import AdminLoggingMiddleware
from app.dependencies.database import get_db
from app.exceptions import BusinessException
from app.middleware.plugin_middleware import PluginMiddleware


def create_fastapi_app(lifespan=None) -> FastAPI:
    """
    创建并配置 FastAPI 应用实例

    Args:
        lifespan: 应用生命周期管理器

    Returns:
        FastAPI: 配置好的 FastAPI 应用实例
    """
    app_kwargs = {
        "title": settings.PROJECT_NAME,
        "version": settings.VERSION or "1.0.0",
        "openapi_url": f"{settings.API_ADMIN_STR}/openapi.json",
        "docs_url": None,  # 禁用默认的 Swagger UI
        "redoc_url": None,  # 禁用默认的 ReDoc
    }

    if lifespan:
        app_kwargs["lifespan"] = lifespan

    app = FastAPI(**app_kwargs)

    return app


def configure_middleware(app: FastAPI, is_installed: bool = False):
    """
    配置应用中间件

    Args:
        app: FastAPI 应用实例
        is_installed: 是否已安装模式
    """
    # 配置 Babel
    configs = BabelConfigs(
        ROOT_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        BABEL_DEFAULT_LOCALE="en",
        BABEL_TRANSLATION_DIRECTORY="lang",
    )

    # 添加 CORS 中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOW_ORIGINS,
        allow_credentials=settings.ALLOW_CREDENTIALS,
        allow_methods=settings.ALLOW_METHODS,
        allow_headers=settings.ALLOW_HEADERS,
        expose_headers=settings.EXPOSE_HEADERS,
    )

    # 添加 Babel 中间件
    app.add_middleware(BabelMiddleware, babel_configs=configs)

    # 仅在已安装模式下加载需要数据库的中间件
    if is_installed:
        app.add_middleware(AdminLoggingMiddleware)
        app.add_middleware(PluginMiddleware, get_db=get_db)


def configure_exception_handlers(app: FastAPI):
    """
    配置异常处理器

    Args:
        app: FastAPI 应用实例
    """
    from fastapi import HTTPException as StarletteHTTPException
    from fastapi.exceptions import RequestValidationError
    from sqlalchemy.exc import IntegrityError, OperationalError

    # 业务异常处理器（最高优先级）
    app.add_exception_handler(BusinessException, handlers.business_exception_handler)

    # 请求验证错误
    app.add_exception_handler(RequestValidationError, handlers.validation_exception_handler)

    # HTTP 异常
    app.add_exception_handler(StarletteHTTPException, handlers.http_exception_handler)

    # ValueError
    app.add_exception_handler(ValueError, handlers.value_error_exception_handler)

    # 数据库异常
    app.add_exception_handler(IntegrityError, handlers.integrity_error_handler)
    app.add_exception_handler(OperationalError, handlers.operational_error_handler)

    # 通用异常处理器（兜底）
    app.add_exception_handler(Exception, handlers.generic_exception_handler)
