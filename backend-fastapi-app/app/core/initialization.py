"""
数据库和插件初始化模块
"""
from fastapi import FastAPI
from app.dependencies.database import SessionLocal, engine
from app.models import Base
from app.plugins.plugin_manager import PluginManager
from app.utils.log_utils import logger


def initialize_database():
    """
    初始化数据库表
    
    Returns:
        bool: 数据库初始化是否成功
    """
    try:
        logger.info("正在创建数据库表...")
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表创建完成")
        return True
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}")
        return False


def initialize_plugins(app):
    """
    初始化插件系统
    
    Args:
        app: FastAPI 应用实例
        
    Returns:
        bool: 插件初始化是否成功
    """
    try:
        logger.info("正在初始化插件...")
        with SessionLocal() as db:
            plugin_manager = PluginManager(db=db)
            plugin_manager.set_router(app.router)
            plugin_manager.load_enabled_plugins()
        logger.info("插件初始化完成")
        return True
    except Exception as e:
        logger.error(f"插件初始化失败: {str(e)}")
        return False


def initialize_application(app: FastAPI) -> bool:
    """
    完整初始化应用（数据库 + 插件）
    
    Args:
        app: FastAPI 应用实例
        
    Returns:
        bool: 初始化是否成功
    """
    try:
        # 初始化数据库
        db_success = initialize_database()
        if not db_success:
            return False
        
        # 加载 API 路由
        from app.core.router_loader import load_api_routes
        logger.info("正在加载API路由...")
        load_api_routes(app)
        
        # 初始化插件
        plugin_success = initialize_plugins(app)
        if not plugin_success:
            return False
        
        return True
    except Exception as e:
        logger.error(f"应用初始化失败: {str(e)}")
        return False
