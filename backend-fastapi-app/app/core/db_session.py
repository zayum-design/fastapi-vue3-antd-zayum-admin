"""
数据库会话管理改进
提供上下文管理器和依赖注入，确保会话正确关闭

注意：推荐使用 app.dependencies.database 中的新接口
"""

from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.dependencies.database import get_session_factory
from app.utils.log_utils import logger

# 获取会话工厂
SessionLocal = get_session_factory()


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    数据库会话上下文管理器

    使用示例:
        with get_db_session() as db:
            user = db.query(User).first()
            # 自动提交和关闭
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        logger.error("Database error: {str(e)}")
        raise
    except Exception:
        db.rollback()
        logger.error("Unexpected error: {str(e)}")
        raise
    finally:
        db.close()


@contextmanager
def get_db_session_read_only() -> Generator[Session, None, None]:
    """
    只读数据库会话上下文管理器（不自动提交）

    使用示例:
        with get_db_session_read_only() as db:
            users = db.query(User).all()
            # 只读操作，不提交
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        logger.error("Database error: {str(e)}")
        raise
    finally:
        db.close()


class DatabaseSessionManager:
    """
    数据库会话管理器
    用于需要手动管理会话生命周期的场景（如中间件）
    """

    def __init__(self):
        self._session: Session | None = None

    def __enter__(self) -> Session:
        self._session = SessionLocal()
        return self._session

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            try:
                if exc_type is not None:
                    self._session.rollback()
                else:
                    self._session.commit()
            except Exception:
                self._session.rollback()
                logger.error("Session cleanup error: {str(e)}")
            finally:
                self._session.close()
                self._session = None

    @property
    def session(self) -> Session | None:
        return self._session


# 改进的依赖注入函数（保持与原有接口兼容）
def get_db() -> Generator[Session, None, None]:
    """
    获取数据库会话 - FastAPI 依赖注入使用
    确保会话正确关闭

    注意：推荐使用 app.dependencies.database.get_db
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
