# app/dependencies/database.py

import logging
import time
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
            pool_use_lifo=True,  # 使用LIFO（后进先出）策略，更有效地回收连接
            echo=False,
            pool_size=10,  # 增加连接池大小
            max_overflow=20,  # 增加最大溢出连接数
            pool_recycle=1800,  # 30分钟回收连接，避免MySQL wait_timeout问题
            pool_timeout=30,  # 增加连接获取超时时间
            connect_args={
                'connect_timeout': 30,  # 增加连接超时时间
                'read_timeout': 60,  # 增加读取超时时间
                'write_timeout': 60,  # 增加写入超时时间
                'charset': 'utf8mb4',
                'autocommit': True,  # 启用自动提交
                'client_flag': 0,  # 清除可能导致问题的客户端标志
                'sql_mode': 'TRADITIONAL',  # 设置SQL模式
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
    """获取数据库会话 - 简化版本，避免scoped_session可能的问题"""
    global engine
    
    if engine is None:
        raise DatabaseConnectionError("数据库不可用")
    
    max_retries = 3
    retry_count = 0
    db = None
    
    while retry_count < max_retries:
        try:
            # 创建新的会话（不使用scoped_session）
            Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            db = Session()
            
            # 测试连接是否有效
            try:
                db.execute(text("SELECT 1"))
                # 连接测试成功
                break
            except Exception as conn_error:
                logger.warning(f"数据库连接测试失败，尝试重新连接 (尝试 {retry_count + 1}/{max_retries}): {str(conn_error)}")
                # 关闭当前会话
                try:
                    db.close()
                except:
                    pass
                
                # 如果是最后一次重试，抛出异常
                if retry_count == max_retries - 1:
                    raise DatabaseConnectionError(f"数据库连接失败: {str(conn_error)}")
                
                # 尝试重新创建引擎
                try:
                    if engine:
                        engine.dispose()
                    engine = create_db_engine()
                    logger.info("数据库引擎已重新创建")
                except Exception as reconnect_error:
                    logger.error(f"数据库重新连接失败: {str(reconnect_error)}")
                    if retry_count == max_retries - 1:
                        raise DatabaseConnectionError(f"数据库连接失败: {str(reconnect_error)}")
                
                retry_count += 1
                # 短暂等待后重试
                time.sleep(0.2 * retry_count)
                continue
                
        except Exception as e:
            logger.error(f"创建数据库会话失败 (尝试 {retry_count + 1}/{max_retries}): {str(e)}")
            if retry_count == max_retries - 1:
                raise DatabaseConnectionError(f"无法创建数据库会话: {str(e)}")
            retry_count += 1
            time.sleep(0.2 * retry_count)
            continue
    
    if db is None:
        raise DatabaseConnectionError("无法创建数据库会话")
    
    try:
        yield db
    except Exception as e:
        # 如果是 HTTPException（如验证码错误），直接重新抛出
        from fastapi import HTTPException
        if isinstance(e, HTTPException):
            raise e
        
        # 检查是否是数据库连接错误
        import pymysql
        from sqlalchemy.exc import DBAPIError, OperationalError, InternalError
        
        # 检查是否是pymysql的错误
        is_pymysql_error = False
        if hasattr(e, 'orig'):
            error_orig = getattr(e, 'orig', None)
            if isinstance(error_orig, (pymysql.err.OperationalError, pymysql.err.InternalError, 
                                      pymysql.err.ProgrammingError, pymysql.err.InterfaceError)):
                is_pymysql_error = True
        
        # 如果是数据库连接错误，记录并抛出
        if isinstance(e, (DBAPIError, OperationalError, InternalError)) or is_pymysql_error:
            logger.warning(f"查询执行过程中数据库连接错误: {str(e)}")
            raise DatabaseConnectionError(f"数据库会话无效: {str(e)}")
        else:
            # 其他异常
            logger.error(f"数据库会话错误: {str(e)}")
            raise DatabaseConnectionError(f"数据库会话无效: {str(e)}")
    finally:
        try:
            if db:
                db.close()
        except Exception as close_error:
            # 忽略关闭时的错误
            logger.debug(f"关闭数据库会话时出错: {str(close_error)}")

# 配置SQLAlchemy日志
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
