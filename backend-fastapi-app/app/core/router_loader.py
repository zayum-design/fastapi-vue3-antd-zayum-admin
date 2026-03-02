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
    # 加载admin相关的API路由
    load_module_api_routes(app, "admin", "/api/admin")

    # 加载common相关的API路由
    load_module_api_routes(app, "common", "/api/common")

    # 加载user相关的API路由
    load_module_api_routes(app, "user", "/api/user")


def load_module_api_routes(app: FastAPI, module_type: str, prefix: str):
    """
    加载指定模块类型的API路由

    Args:
        app: FastAPI 应用实例
        module_type: 模块类型 (admin/common/user)
        prefix: 路由前缀
    """
    if module_type == "admin":
        # admin模块有特殊的目录结构
        modules_dir = os.path.join(os.path.dirname(__file__), "..", "modules", "admin")

        if not os.path.isdir(modules_dir):
            logger.warning("Admin服务目录不存在: {modules_dir}")
            return

        # 遍历所有sys_*目录和auth目录
        for item in os.listdir(modules_dir):
            item_path = os.path.join(modules_dir, item)
            if os.path.isdir(item_path) and (item.startswith("sys_") or item == "auth"):
                api_dir = os.path.join(item_path, "api")
                if os.path.isdir(api_dir):
                    # 加载api目录下的所有.py文件
                    for file in os.listdir(api_dir):
                        if file.endswith(".py") and file != "__init__.py":
                            module_name = file[:-3]
                            module_path = f"app.modules.admin.{item}.api.{module_name}"
                            try:
                                module = importlib.import_module(module_path)
                                if hasattr(module, "router"):
                                    router = module.router
                                    app.include_router(router, prefix=prefix)
                                    logger.info("已加载API路由: {module_path}")
                            except ModuleNotFoundError:
                                logger.info("模块导入失败: {module_path}, 错误信息: {e}")
                            except Exception:
                                logger.error("加载API路由时出错: {module_path}, 错误: {e}")
    else:
        # common和user模块有简单的目录结构
        api_dir = os.path.join(os.path.dirname(__file__), "..", "modules", module_type, "api")

        if not os.path.isdir(api_dir):
            logger.warning("{module_type.capitalize()} API目录不存在: {api_dir}")
            return

        for file in os.listdir(api_dir):
            if file.endswith(".py") and file != "__init__.py":
                module_name = file[:-3]
                module_path = f"app.modules.{module_type}.api.{module_name}"
                try:
                    module = importlib.import_module(module_path)
                    if hasattr(module, "router"):
                        router = module.router
                        app.include_router(router, prefix=prefix)
                        logger.info("已加载{module_type.capitalize()} API路由: {module_path}")
                except ModuleNotFoundError:
                    logger.info(
                        "{module_type.capitalize()}模块导入失败: {module_path}, 错误信息: {e}"
                    )
                except Exception:
                    logger.error(
                        "加载{module_type.capitalize()} API路由时出错: {module_path}, 错误: {e}"
                    )


def load_installation_routes(app: FastAPI):
    """
    加载安装相关的路由

    Args:
        app: FastAPI 应用实例
    """
    from install.install_check import router as install_check

    app.include_router(install_check, prefix="/api", tags=["installation Check"])


def load_install_routes(app: FastAPI):
    """
    加载完整的安装路由

    Args:
        app: FastAPI 应用实例
    """
    from install.install import router as install_router

    app.include_router(install_router, prefix="/api/install", tags=["installation"])
