"""
应用生命周期管理模块
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.utils.log_utils import logger
from app.core.environment import check_environment, is_application_installed
from app.core.router_loader import load_installation_routes, load_install_routes
from app.core.initialization import initialize_application


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("应用启动中...")
    
    # 检查环境配置
    check_environment()
    
    # 加载安装检查路由
    load_installation_routes(app)
    
    # 检查是否已安装
    is_installed = is_application_installed()
    
    if not is_installed:
        logger.info("未找到install.lock，仅加载安装路由")
        load_install_routes(app)
    else:
        logger.info("检测到install.lock，执行完整初始化")
        app.state.db_available = False
        
        try:
            from app.dependencies.database import engine
            if engine is not None:
                # 执行完整初始化
                init_success = initialize_application(app)
                app.state.db_available = init_success
            else:
                logger.error("数据库引擎未初始化")
                app.state.db_available = False
            
        except Exception as e:
            logger.error(f"启动过程中发生错误: {str(e)}")
            app.state.db_available = False

    yield  # 应用运行阶段

    logger.info("应用关闭中...")
