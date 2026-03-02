"""
数据库依赖管理模块
提供同步和异步数据库会话管理
"""

import logging
import time
from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.utils.log_utils import logger

# ==================== 同步数据库配置 ====================


class DatabaseConnectionError(Exception):
    """数据库连接错误"""

    pass


# 引擎和会话工厂（全局单例）
_engine = None
_SessionFactory = None


def get_engine():
    """获取或创建数据库引擎（单例模式）"""
    global _engine

    if _engine is None:
        try:
            _engine = create_engine(
                settings.DATABASE_URL,
                pool_pre_ping=True,
                pool_use_lifo=True,
                echo=settings.DEBUG,
                pool_size=10,
                max_overflow=20,
                pool_recycle=1800,
                pool_timeout=30,
                connect_args={
                    "connect_timeout": 30,
                    "read_timeout": 60,
                    "write_timeout": 60,
                    "charset": "utf8mb4",
                    "autocommit": True,
                    "client_flag": 0,
                    "sql_mode": "TRADITIONAL",
                },
            )
            logger.info("Database engine created")
        except Exception as e:
            logger.error("数据库引擎创建失败: {str(e)}")
            raise DatabaseConnectionError(f"数据库配置错误: {e!s}")

    return _engine


def get_session_factory() -> sessionmaker:
    """获取会话工厂（单例模式）"""
    global _SessionFactory

    if _SessionFactory is None:
        engine = get_engine()
        _SessionFactory = sessionmaker(
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,  # 防止 commit 后对象过期，避免 "0 were matched" 错误
            bind=engine,
        )

    return _SessionFactory


def check_db_connection() -> bool:
    """检查数据库连接"""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        logger.error("数据库连接检查失败: {str(e)}")
        return False


# ==================== FastAPI Depends 依赖 ====================


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI Depends 依赖：获取数据库会话

    Usage:
        @router.get("/items")
        def get_items(db: Session = Depends(get_db)):
            ...
    """
    factory = get_session_factory()
    db = factory()

    try:
        # 测试连接有效性
        db.execute(text("SELECT 1"))
        yield db
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        logger.error("数据库会话错误: {str(e)}")
        raise DatabaseConnectionError(f"数据库会话错误: {e!s}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# ==================== 上下文管理器（推荐用于后台任务） ====================


@contextmanager
def db_session() -> Generator[Session, None, None]:
    """
    数据库会话上下文管理器
    推荐用于后台任务、脚本等非请求上下文场景

    Usage:
        with db_session() as db:
            result = db.query(Model).all()
            # 自动提交或回滚
    """
    factory = get_session_factory()
    db = factory()

    try:
        yield db
        db.commit()
        logger.debug("Database session committed")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error("Database session error: {str(e)}")
        raise DatabaseConnectionError(f"数据库会话错误: {e!s}")
    except Exception:
        db.rollback()
        logger.error("Unexpected error in db_session: {str(e)}")
        raise
    finally:
        db.close()


@contextmanager
def db_session_safe(max_retries: int = 3) -> Generator[Session | None, None, None]:
    """
    带重试机制的数据库会话上下文管理器

    Usage:
        with db_session_safe(max_retries=3) as db:
            if db is None:
                # 处理连接失败
                return
            result = db.query(Model).all()
    """
    factory = get_session_factory()
    last_exception = None

    for attempt in range(max_retries):
        db = None
        try:
            db = factory()
            # 测试连接
            db.execute(text("SELECT 1"))
            yield db
            db.commit()
            return
        except SQLAlchemyError as e:
            last_exception = e
            if db:
                db.rollback()
            logger.warning("数据库会话尝试 {attempt + 1}/{max_retries} 失败: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(0.2 * (attempt + 1))
        except Exception:
            if db:
                db.rollback()
            raise
        finally:
            if db:
                db.close()

    # 所有重试都失败了
    logger.error("数据库会话在 {max_retries} 次尝试后仍然失败: {str(last_exception)}")
    yield None


# ==================== 高级会话管理器 ====================


class DatabaseManager:
    """
    数据库管理器
    提供高级数据库操作功能
    """

    def __init__(self):
        self._engine = None
        self._session_factory = None

    @property
    def engine(self):
        if self._engine is None:
            self._engine = get_engine()
        return self._engine

    @property
    def session_factory(self):
        if self._session_factory is None:
            self._session_factory = get_session_factory()
        return self._session_factory

    def session(self) -> Session:
        """获取新会话（需手动管理）"""
        return self.session_factory()

    def close(self):
        """关闭数据库连接"""
        global _engine, _SessionFactory

        if _engine:
            _engine.dispose()
            _engine = None
            _SessionFactory = None
            logger.info("Database engine disposed")


# 全局数据库管理器实例
db_manager = DatabaseManager()


# ==================== 初始化检查 ====================


def init_database():
    """初始化数据库连接"""
    try:
        engine = get_engine()
        if check_db_connection():
            logger.info("数据库连接成功")
            return True
        else:
            logger.error("数据库连接失败")
            return False
    except Exception:
        logger.error("数据库初始化失败: {str(e)}")
        return False


# 配置 SQLAlchemy 日志
logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(
    logging.WARNING if not settings.DEBUG else logging.INFO
)
