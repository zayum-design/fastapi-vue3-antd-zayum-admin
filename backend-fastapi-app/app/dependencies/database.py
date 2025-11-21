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
            pool_pre_ping=True,  # 在从连接池获取连接前执行ping测试
            echo=False,
            pool_size=5,  # 增加连接池大小
            max_overflow=10,  # 增加最大溢出连接数
            pool_recycle=3600,  # 1小时回收连接，避免MySQL wait_timeout问题
            pool_timeout=30,  # 增加连接获取超时时间
            connect_args={
                'connect_timeout': 15,  # 增加连接超时时间
                'read_timeout': 30,  # 增加读取超时时间
                'write_timeout': 30,  # 增加写入超时时间
                'charset': 'utf8mb4',
                'autocommit': True,  # 启用自动提交
                'client_flag': 0,  # 清除可能导致问题的客户端标志
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
        # 测试连接是否有效
        db.execute(text("SELECT 1"))
        yield db
    except Exception as e:
        # 如果连接无效，关闭并重新创建
        db.close()
        # 如果是 HTTPException（如验证码错误），直接重新抛出
        from fastapi import HTTPException
        if isinstance(e, HTTPException):
            raise e
        # 其他异常包装为数据库连接错误
        raise DatabaseConnectionError(f"数据库会话无效: {str(e)}")
    finally:
        db.close()

# 配置SQLAlchemy日志
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
