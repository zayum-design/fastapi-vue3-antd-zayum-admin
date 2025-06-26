# app/dependencies/database.py

import logging
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.sql import text
from app.core.config import settings
from app.utils.log_utils import logger

class DatabaseConnectionError(Exception):
    """自定义数据库连接错误异常"""
    pass

def create_db_engine():
    """创建数据库引擎"""
    try:
        engine = create_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True,
            echo=False,
            connect_args={
                'connect_timeout': 5
            }
        )
        return engine
    except Exception as e:
        logger.error(f"数据库引擎创建失败: {str(e)}")
        raise DatabaseConnectionError(f"数据库配置错误: {str(e)}")

def check_db_connection(engine):
    """检查数据库连接"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"数据库连接失败: {str(e)}")
        raise DatabaseConnectionError(f"无法连接到数据库: {str(e)}")

# 初始化数据库引擎和会话工厂
engine = None
SessionLocal = None

try:
    engine = create_db_engine()
    check_db_connection(engine)
    SessionLocal = scoped_session(
        sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine
        )
    )
    logger.info("数据库连接成功")
except DatabaseConnectionError as e:
    logger.error(f"数据库初始化失败: {str(e)}")
    # 不终止程序，继续运行但标记为不可用状态

def get_db():
    """获取数据库会话"""
    if SessionLocal is None:
        raise DatabaseConnectionError("数据库不可用")
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 配置SQLAlchemy日志
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)