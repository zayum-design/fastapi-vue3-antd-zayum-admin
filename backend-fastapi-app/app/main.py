# app/main.py

import importlib
import os
import shutil
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError,HTTPException as StarletteHTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi_babel import Babel, BabelConfigs, BabelMiddleware
from app.core.middleware import AdminLoggingMiddleware
from app.core.handlers import (
    validation_exception_handler,
    http_exception_handler,
    value_error_exception_handler,
    generic_exception_handler,
    integrity_error_handler,
    operational_error_handler
)
from sqlalchemy.exc import OperationalError, IntegrityError

from app.core.config import settings
from app.dependencies.database import SessionLocal, engine, get_db
from app.models import Base
from app.middleware.plugin_middleware import PluginMiddleware
from app.plugins.plugin_manager import PluginManager
from app.utils.log_utils import logger
from app.install.install_check import router as install_check

# Check if application is installed (install.lock exists)
install_lock_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "install.lock")
is_installed = os.path.exists(install_lock_path)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("应用启动中...")
    
    # 检查并确保.env文件存在且有效
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(root_dir, ".env")
    env_example_path = os.path.join(root_dir, ".env.example")
    
    if not os.path.exists(env_path):
        if os.path.exists(env_example_path):
            try:
                shutil.copyfile(env_example_path, env_path)
                # 确保文件写入完成
                with open(env_path, 'r') as f:
                    content = f.read()
                    if not content:
                        raise ValueError("创建.env文件失败，内容为空")
                logger.info("已从.env.example创建.env文件")
            except Exception as e:
                logger.error(f"创建.env文件失败: {str(e)}")
                raise
        else:
            logger.error("缺少.env.example文件，无法创建.env")
            raise FileNotFoundError("缺少.env.example文件")
    else:
        # 验证.env文件是否包含必要配置
        with open(env_path, 'r') as f:
            content = f.read()
            required_keys = ['MYSQL_USER', 'MYSQL_PASSWORD', 'MYSQL_DB', 'MYSQL_HOST', 'MYSQL_PORT']
            missing_keys = [key for key in required_keys if f"{key}=" not in content]
            if missing_keys:
                logger.error(f".env文件缺少必要配置: {', '.join(missing_keys)}")
                raise ValueError(f"缺少必要配置: {', '.join(missing_keys)}")

    app.include_router(install_check, prefix="/api", tags=["installation Check"])
        
    if not os.path.exists(install_lock_path):
        from app.install.install import router as install_router
        logger.info("未找到install.lock，仅加载安装路由")
        app.include_router(install_router, prefix="/api/install", tags=["installation"])
    else:
        logger.info("检测到install.lock，执行完整初始化")
        app.state.db_available = False
        
        try:
            if engine is not None:
                logger.info("正在加载API路由...")
                load_apis()
                logger.info("正在创建数据库表...")
                Base.metadata.create_all(bind=engine)
                logger.info("数据库表创建完成")
                logger.info("正在初始化插件...")
                initialize_plugins()
                logger.info("插件初始化完成")
                app.state.db_available = True
            
        except Exception as e:
            logger.error(f"启动过程中发生错误: {str(e)}")

    yield  # 应用运行阶段
  
    logger.info("应用关闭中..")  

# 初始化 FastAPI 应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    openapi_url=f"{settings.API_ADMIN_STR}/openapi.json",
    lifespan=lifespan
)

# 配置 Babel
configs = BabelConfigs(
    ROOT_DIR=os.path.dirname(os.path.abspath(__file__)),
    BABEL_DEFAULT_LOCALE="en",
    BABEL_TRANSLATION_DIRECTORY="lang",
)
babel = Babel(configs=configs)

# 添加中间件和异常处理器
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://demo.zayumadmin.com","http://zayumadmin.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*", "X-Captcha-Id"],
    expose_headers=["X-Captcha-Id"]
)
app.add_middleware(BabelMiddleware, babel_configs=configs)

# 仅在已安装模式下加载需要数据库的中间件
if is_installed:
    app.add_middleware(AdminLoggingMiddleware)
    app.add_middleware(PluginMiddleware, get_db=get_db)

# 添加异常处理器
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(ValueError, value_error_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)
app.add_exception_handler(OperationalError, operational_error_handler)

def load_apis():
    api_directory = os.path.join(os.path.dirname(__file__), 'api')
    
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

def initialize_plugins():
    with SessionLocal() as db:
        plugin_manager = PluginManager(db=db)
        plugin_manager.set_router(app.router)
        plugin_manager.load_enabled_plugins()
