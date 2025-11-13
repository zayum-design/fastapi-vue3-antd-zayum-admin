"""
API 路由加载模块
"""
import importlib
import os
from fastapi import FastAPI
from app.utils.log_utils import logger


def load_api_routes(app: FastAPI):
    """
    动态加载所有 API 路由
    
    Args:
        app: FastAPI 应用实例
    """
    api_directory = os.path.join(os.path.dirname(__file__), '..', 'api')
    
    if not os.path.isdir(api_directory):
        raise Exception(f"API目录不存在: {api_directory}")

    for root, dirs, files in os.walk(api_directory):
        for file in files:
            if file.endswith('.py') and file != '__init__.py':
                module_path = os.path.relpath(os.path.join(root, file), api_directory).replace(os.sep, '.')[:-3]
                logger.info(f"正在导入模块: {module_path}")
                try:
                    module = importlib.import_module(f"app.api.{module_path}")
                    if hasattr(module, "router"):
                        router = getattr(module, "router")
                        prefix = module_path.split('.')[-2] if len(module_path.split('.')) > 1 else module_path.split('.')[0]
                        app.include_router(router, prefix=f"/api/{prefix}")
                except ModuleNotFoundError as e:
                    logger.info(f"模块导入失败: {module_path}, 错误信息: {e}")


def load_installation_routes(app: FastAPI):
    """
    加载安装相关的路由
    
    Args:
        app: FastAPI 应用实例
    """
    from app.install.install_check import router as install_check
    app.include_router(install_check, prefix="/api", tags=["installation Check"])


def load_install_routes(app: FastAPI):
    """
    加载完整的安装路由
    
    Args:
        app: FastAPI 应用实例
    """
    from app.install.install import router as install_router
    app.include_router(install_router, prefix="/api/install", tags=["installation"])
