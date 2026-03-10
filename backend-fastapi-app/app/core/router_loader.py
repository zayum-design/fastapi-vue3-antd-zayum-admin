"""
API 路由加载模块
按目录结构自动扫描和加载API路由
"""

import importlib
from pathlib import Path

from fastapi import FastAPI

from app.utils.log_utils import logger


def load_api_routes(app: FastAPI):
    """
    动态加载所有 API 路由
    从 app/api/ 下的所有版本目录(v1, v2等)自动扫描所有API文件

    Args:
        app: FastAPI 应用实例
    """
    # API根目录
    api_dir = Path(__file__).parent.parent / "api"

    if not api_dir.exists():
        logger.warning(f"API目录不存在: {api_dir}")
        return

    # 遍历 api 下的所有版本目录 (v1, v2等)
    for version_dir in api_dir.iterdir():
        if version_dir.is_dir() and not version_dir.name.startswith("__"):
            version = version_dir.name  # v1, v2, ...
            # 遍历版本目录下的所有模块目录 (admin, common, user等)
            for module_dir in version_dir.iterdir():
                if module_dir.is_dir() and not module_dir.name.startswith("__"):
                    module_name = module_dir.name
                    # 计算路由前缀: /api/{version}/{module_name}
                    prefix = f"/api/{version}/{module_name}"
                    # 加载该模块下的所有API路由
                    load_module_api_routes(
                        app, module_dir, prefix, f"app.api.{version}.{module_name}"
                    )


def load_module_api_routes(app: FastAPI, module_dir: Path, prefix: str, module_base_path: str):
    """
    加载指定模块目录下的所有API路由

    Args:
        app: FastAPI 应用实例
        module_dir: 模块目录路径
        prefix: 路由前缀
        module_base_path: Python模块基础路径
    """
    if not module_dir.is_dir():
        return

    # 遍历目录下的所有.py文件
    for file_path in module_dir.iterdir():
        if file_path.is_file() and file_path.suffix == ".py" and file_path.stem != "__init__":
            module_name = file_path.stem
            module_import_path = f"{module_base_path}.{module_name}"

            try:
                module = importlib.import_module(module_import_path)
                if hasattr(module, "router"):
                    router = module.router
                    app.include_router(router, prefix=prefix)
                    logger.info(f"已加载API路由: {module_import_path} -> {prefix}")
            except ModuleNotFoundError as e:
                logger.warning(f"模块导入失败: {module_import_path}, 错误信息: {e}")
            except Exception as e:
                logger.error(f"加载API路由时出错: {module_import_path}, 错误: {e}")


def load_installation_routes(app: FastAPI):
    """
    加载安装检查相关的路由

    Args:
        app: FastAPI 应用实例
    """
    from app.api.v1.common.install import install_check_router

    app.include_router(install_check_router, prefix="/api", tags=["installation Check"])


def load_install_routes(app: FastAPI):
    """
    加载完整的安装路由

    Args:
        app: FastAPI 应用实例
    """
    from app.api.v1.common.install import install_router

    app.include_router(install_router, prefix="/api/install", tags=["installation"])
