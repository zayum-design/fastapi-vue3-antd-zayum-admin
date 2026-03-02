"""
Service 层基类
提供业务逻辑处理的基础功能
"""

from collections.abc import Callable
from contextlib import contextmanager
from functools import wraps
from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.exceptions import BusinessException
from app.repositories.base import BaseRepository
from app.utils.log_utils import logger

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class ServiceError(BusinessException):
    """Service 层错误"""

    pass


class Transactional:
    """
    事务管理装饰器

    Usage:
        class MyService(BaseService):
            @Transactional()
            def create_with_related(self, db: Session, data: dict):
                # 这里的操作会在事务中执行
                obj = self.create(db, data)
                # 其他相关操作...
                return obj
    """

    def __init__(self, rollback_on: tuple = (Exception,)):
        """
        Args:
            rollback_on: 触发回滚的异常类型元组
        """
        self.rollback_on = rollback_on

    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 获取 db session（假设是第一个参数或 kwargs 中的 db）
            db = kwargs.get("db")
            if db is None and len(args) > 1:
                db = args[1]  # self 是 args[0]

            if db is None:
                raise ServiceError("Database session is required for transactional operation")

            try:
                result = func(*args, **kwargs)
                db.commit()
                return result
            except self.rollback_on:
                db.rollback()
                logger.error("Transaction rolled back due to: {e}")
                raise

        return wrapper


@contextmanager
def service_transaction(db: Session):
    """
    事务上下文管理器

    Usage:
        with service_transaction(db) as tx_db:
            service.create(tx_db, data)
            # 其他操作...
    """
    try:
        yield db
        db.commit()
        logger.debug("Transaction committed")
    except Exception:
        db.rollback()
        logger.error("Transaction rolled back: {e}")
        raise


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Service 层基类

    提供标准化的业务逻辑处理，职责：
    1. 处理业务规则验证
    2. 协调多个 Repository 操作
    3. 管理事务边界
    4. 业务事件触发

    Usage:
        class UserService(BaseService[User, UserCreate, UserUpdate]):
            def __init__(self):
                super().__init__(UserRepository())

            def create(self, db: Session, obj_in: UserCreate) -> User:
                # 业务验证
                if not self._validate_email(obj_in.email):
                    raise ServiceError("Invalid email")

                # 调用 Repository 创建
                return super().create(db, obj_in)
    """

    def __init__(self, repository: BaseRepository[ModelType, CreateSchemaType, UpdateSchemaType]):
        self._repo = repository

    # ========== 基础 CRUD 委托给 Repository ==========

    def get(self, db: Session, id: Any) -> ModelType | None:
        """通过 ID 获取"""
        return self._repo.get(db, id)

    def get_or_404(self, db: Session, id: Any) -> ModelType:
        """通过 ID 获取，不存在则抛出异常"""
        return self._repo.get_or_404(db, id)

    def get_by(self, db: Session, **kwargs) -> ModelType | None:
        """通过字段获取"""
        return self._repo.get_by(db, **kwargs)

    def get_multi(
        self,
        db: Session,
        *,
        page: int = 1,
        per_page: int = 20,
        search: str | None = None,
        order_by: list[str] | str | None = None,
    ) -> list[ModelType]:
        """获取多条记录"""
        return self._repo.get_multi(
            db, page=page, per_page=per_page, search=search, order_by=order_by
        )

    def get_multi_with_total(
        self,
        db: Session,
        *,
        page: int = 1,
        per_page: int = 10,
        search: str | None = None,
        orderby: str | None = None,
    ) -> tuple[list[ModelType], int]:
        """获取分页数据和总数"""
        return self._repo.get_multi_with_total(
            db, page=page, per_page=per_page, search=search, orderby=orderby
        )

    def get_all(
        self, db: Session, *, search: str | None = None, order_by: list[str] | str | None = None
    ) -> list[ModelType]:
        """获取所有记录"""
        return self._repo.get_all(db, search=search, order_by=order_by)

    def count(self, db: Session, search: str | None = None) -> int:
        """获取记录数量"""
        return self._repo.count(db, search=search)

    def create(self, db: Session, obj_in: CreateSchemaType | dict[str, Any]) -> ModelType:
        """创建记录"""
        # 子类可以在这里添加业务验证
        return self._repo.create(db, obj_in)

    def update(
        self, db: Session, db_obj: ModelType, obj_in: UpdateSchemaType | dict[str, Any]
    ) -> ModelType:
        """更新记录"""
        return self._repo.update(db, db_obj, obj_in)

    def delete(self, db: Session, id: Any) -> ModelType:
        """删除记录"""
        return self._repo.delete(db, id)

    def remove(self, db: Session, id: Any) -> ModelType | None:
        """删除记录（兼容旧版接口）"""
        return self._repo.remove(db, id)

    def bulk_create(
        self, db: Session, objs_in: list[CreateSchemaType | dict[str, Any]]
    ) -> list[ModelType]:
        """批量创建"""
        return self._repo.bulk_create(db, objs_in)

    def bulk_delete(self, db: Session, ids: list[Any]) -> int:
        """批量删除"""
        return self._repo.bulk_delete(db, ids)

    # ========== 查询构建器 ==========

    def query(self, db: Session):
        """获取查询构建器"""
        return self._repo.query(db)

    # ========== 业务工具方法 ==========

    def exists(self, db: Session, id: Any) -> bool:
        """检查记录是否存在"""
        return self._repo.get(db, id) is not None

    def exists_by(self, db: Session, **kwargs) -> bool:
        """检查是否存在符合条件的记录"""
        return self._repo.get_by(db, **kwargs) is not None


class CrudService(BaseService[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    简化版 CRUD Service
    自动创建 Repository，适合简单的 CRUD 场景

    Usage:
        class UserService(CrudService[User, UserCreate, UserUpdate]):
            DEFAULT_SEARCH_FIELDS = ['username', 'email']
            DEFAULT_UNIQUE_FIELDS = ['username', 'email']
    """

    # 默认搜索字段，子类可覆盖
    DEFAULT_SEARCH_FIELDS: list[str] = []

    # 默认唯一字段，子类可覆盖
    DEFAULT_UNIQUE_FIELDS: list[str] = []

    def __init__(self, model_class: type[ModelType]):
        from app.repositories.base import create_repository_class

        repo_class = create_repository_class(
            model_class,
            search_fields=self.DEFAULT_SEARCH_FIELDS,
            unique_fields=self.DEFAULT_UNIQUE_FIELDS,
        )
        super().__init__(repo_class())
