"""
通用 Repository 基类
提供标准化的 CRUD 操作和数据访问模式
"""

from typing import Any, Generic, TypeVar

from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy import asc, desc, or_
from sqlalchemy.orm import Query, Session

from app.dependencies.database import get_db
from app.exceptions import ConflictError, DatabaseError, NotFoundError
from app.utils.log_utils import logger

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class RepositoryError(Exception):
    """Repository 层错误"""

    pass


class QueryBuilder(Generic[ModelType]):
    """
    查询构建器
    支持链式调用和复杂查询构建
    """

    def __init__(self, model: type[ModelType], query: Query, repository: "BaseRepository"):
        self._model = model
        self._query = query
        self._repository = repository

    def filter(self, *criterion) -> "QueryBuilder[ModelType]":
        """添加过滤条件"""
        self._query = self._query.filter(*criterion)
        return self

    def filter_by(self, **kwargs) -> "QueryBuilder[ModelType]":
        """按字段过滤"""
        self._query = self._query.filter_by(**kwargs)
        return self

    def search(
        self, search_term: str, fields: list[str] | None = None
    ) -> "QueryBuilder[ModelType]":
        """
        全文搜索

        Args:
            search_term: 搜索关键词
            fields: 要搜索的字段列表，None 使用模型默认搜索字段
        """
        if not search_term:
            return self

        search_fields = fields or self._repository.get_searchable_fields()
        if not search_fields:
            return self

        search_pattern = f"%{search_term}%"
        filters = []

        for field_name in search_fields:
            if hasattr(self._model, field_name):
                field = getattr(self._model, field_name)
                filters.append(field.ilike(search_pattern))

        if filters:
            self._query = self._query.filter(or_(*filters))

        return self

    def order_by(self, *fields: str) -> "QueryBuilder[ModelType]":
        """
        排序

        Args:
            fields: 排序字段，前缀 - 表示降序，如 "-created_at"
        """
        order_clauses = []

        for field in fields:
            if field.startswith("-"):
                # 降序
                field_name = field[1:]
                if hasattr(self._model, field_name):
                    order_clauses.append(desc(getattr(self._model, field_name)))
            else:
                # 升序
                if hasattr(self._model, field):
                    order_clauses.append(asc(getattr(self._model, field)))

        if order_clauses:
            self._query = self._query.order_by(*order_clauses)

        return self

    def order_by_string(self, orderby: str | None) -> "QueryBuilder[ModelType]":
        """
        支持字符串格式的排序，如 "name_asc", "created_at_desc"

        Args:
            orderby: 排序字符串，格式为 "field_direction"
        """
        if not orderby:
            return self

        try:
            # 处理多种分隔符: _desc, _asc, -desc, -asc
            if "_" in orderby:
                field, direction = orderby.rsplit("_", 1)
            elif orderby.endswith("Desc") or orderby.endswith("Asc"):
                if orderby.endswith("Desc"):
                    field = orderby[:-4]
                    direction = "desc"
                else:
                    field = orderby[:-3]
                    direction = "asc"
            else:
                field = orderby
                direction = "asc"

            if not hasattr(self._model, field):
                logger.warning("排序字段不存在: {field}")
                return self

            order_column = getattr(self._model, field)
            if direction.lower() == "asc":
                self._query = self._query.order_by(asc(order_column))
            elif direction.lower() == "desc":
                self._query = self._query.order_by(desc(order_column))
            else:
                logger.warning("无效的排序方向: {direction}")

        except ValueError:
            logger.error("无效的排序格式: {orderby}")

        return self

    def paginate(self, page: int = 1, per_page: int = 20) -> "QueryBuilder[ModelType]":
        """分页"""
        page = max(1, page)
        per_page = max(1, min(per_page, 100))  # 限制最大 100 条

        self._query = self._query.offset((page - 1) * per_page).limit(per_page)
        return self

    def all(self) -> list[ModelType]:
        """获取所有结果"""
        return self._query.all()

    def first(self) -> ModelType | None:
        """获取第一条结果"""
        return self._query.first()

    def one(self) -> ModelType:
        """获取单条结果，不存在则抛出异常"""
        result = self._query.one_or_none()
        if result is None:
            raise NotFoundError(f"{self._model.__name__} not found")
        return result

    def count(self) -> int:
        """获取结果数量"""
        return self._query.count()

    def exists(self) -> bool:
        """检查是否存在"""
        return self._query.first() is not None


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    通用 Repository 基类

    提供标准化的 CRUD 操作，支持：
    - 基础 CRUD
    - 搜索和过滤
    - 分页
    - 批量操作
    - 唯一性验证

    子类可覆盖 DEFAULT_SEARCH_FIELDS 和 DEFAULT_UNIQUE_FIELDS
    """

    # 默认搜索字段，子类可覆盖
    DEFAULT_SEARCH_FIELDS: list[str] = []

    # 默认唯一字段，子类可覆盖
    DEFAULT_UNIQUE_FIELDS: list[str] = []

    def __init__(self, model: type[ModelType]):
        self._model = model
        self._searchable_fields: list[str] = self.DEFAULT_SEARCH_FIELDS.copy()
        self._unique_fields: list[str] = self.DEFAULT_UNIQUE_FIELDS.copy()

    def set_searchable_fields(self, fields: list[str]) -> "BaseRepository":
        """设置可搜索字段"""
        self._searchable_fields = fields
        return self

    def set_unique_fields(self, fields: list[str]) -> "BaseRepository":
        """设置唯一字段"""
        self._unique_fields = fields
        return self

    def get_searchable_fields(self) -> list[str]:
        """获取可搜索字段"""
        return self._searchable_fields

    # ========== 基础 CRUD ==========

    def get(self, db: Session, id: Any) -> ModelType | None:
        """通过 ID 获取"""
        return db.get(self._model, id)

    def get_or_404(self, db: Session, id: Any) -> ModelType:
        """通过 ID 获取，不存在则抛出异常"""
        obj = self.get(db, id)
        if obj is None:
            raise NotFoundError(f"{self._model.__name__} with id={id} not found")
        return obj

    def get_by(self, db: Session, **kwargs) -> ModelType | None:
        """通过字段获取"""
        return db.query(self._model).filter_by(**kwargs).first()

    def get_multi(
        self,
        db: Session,
        *,
        page: int = 1,
        per_page: int = 20,
        search: str | None = None,
        order_by: list[str] | str | None = None,
    ) -> list[ModelType]:
        """
        获取多条记录（支持字符串或列表格式的排序）

        Args:
            order_by: 排序参数，可以是列表 ["-created_at", "name"] 或字符串 "created_at_desc"
        """
        query = self.query(db)

        if search:
            query = query.search(search)

        if order_by:
            if isinstance(order_by, str):
                # 字符串格式: "field_asc" 或 "field_desc"
                query = query.order_by_string(order_by)
            else:
                # 列表格式: ["-created_at", "name"]
                query = query.order_by(*order_by)

        return query.paginate(page, per_page).all()

    def get_all(
        self, db: Session, *, search: str | None = None, order_by: list[str] | str | None = None
    ) -> list[ModelType]:
        """获取所有记录"""
        query = self.query(db)

        if search:
            query = query.search(search)

        if order_by:
            if isinstance(order_by, str):
                query = query.order_by_string(order_by)
            else:
                query = query.order_by(*order_by)

        return query.all()

    def get_multi_with_total(
        self,
        db: Session,
        *,
        page: int = 1,
        per_page: int = 10,
        search: str | None = None,
        orderby: str | None = None,
    ) -> tuple[list[ModelType], int]:
        """
        获取分页数据和总数（一次性查询，减少数据库往返）

        Returns:
            Tuple[数据列表, 总数]
        """
        page = max(1, page)
        per_page = max(1, min(per_page, 100))

        query = self.query(db)

        if search:
            query = query.search(search)

        if orderby:
            query = query.order_by_string(orderby)

        # 获取总数
        total = query.count()

        # 获取分页数据
        items = query.paginate(page, per_page).all()

        return items, total

    def count(self, db: Session, *, search: str | None = None) -> int:
        """获取记录数量"""
        query = self.query(db)

        if search:
            query = query.search(search)

        return query.count()

    # 兼容旧版接口
    def get_total(self, db: Session, search: str | None = None) -> int:
        """获取记录数量（兼容旧版接口）"""
        return self.count(db, search=search)

    def create(self, db: Session, obj_in: CreateSchemaType | dict[str, Any]) -> ModelType:
        """
        创建记录

        Args:
            db: 数据库会话
            obj_in: 创建数据（Pydantic 模型或字典）

        Returns:
            创建的对象
        """
        try:
            # 转换为字典
            if isinstance(obj_in, BaseModel):
                data = obj_in.model_dump(exclude_unset=True)
            else:
                data = obj_in

            # 唯一性检查
            self._check_uniqueness(db, data)

            # 创建对象
            db_obj = self._model(**data)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)

            logger.info(
                f"{self._model.__name__} created",
                extra={"model": self._model.__name__, "id": getattr(db_obj, "id", None)},
            )

            return db_obj

        except Exception as e:
            db.rollback()
            logger.error(
                f"Failed to create {self._model.__name__}",
                extra={"model": self._model.__name__, "error": str(e)},
                exc_info=True,
            )
            raise DatabaseError(f"Failed to create {self._model.__name__}: {e!s}")

    def update(
        self, db: Session, db_obj: ModelType, obj_in: UpdateSchemaType | dict[str, Any]
    ) -> ModelType:
        """
        更新记录

        Args:
            db: 数据库会话
            db_obj: 数据库对象
            obj_in: 更新数据

        Returns:
            更新后的对象
        """
        try:
            # 转换为字典
            if isinstance(obj_in, BaseModel):
                update_data = obj_in.model_dump(exclude_unset=True)
            else:
                update_data = obj_in

            # 唯一性检查（排除当前对象）
            self._check_uniqueness(db, update_data, exclude_id=getattr(db_obj, "id", None))

            # 更新字段
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)

            db.commit()
            db.refresh(db_obj)

            logger.info(
                f"{self._model.__name__} updated",
                extra={"model": self._model.__name__, "id": getattr(db_obj, "id", None)},
            )

            return db_obj

        except Exception as e:
            db.rollback()
            logger.error(
                f"Failed to update {self._model.__name__}",
                extra={
                    "model": self._model.__name__,
                    "id": getattr(db_obj, "id", None),
                    "error": str(e),
                },
                exc_info=True,
            )
            raise DatabaseError(f"Failed to update {self._model.__name__}: {e!s}")

    def delete(self, db: Session, id: Any) -> ModelType:
        """
        删除记录

        Args:
            db: 数据库会话
            id: 记录 ID

        Returns:
            删除的对象
        """
        try:
            obj = self.get_or_404(db, id)
            db.delete(obj)
            db.commit()

            logger.info(
                f"{self._model.__name__} deleted", extra={"model": self._model.__name__, "id": id}
            )

            return obj

        except NotFoundError:
            raise
        except Exception as e:
            db.rollback()
            logger.error(
                f"Failed to delete {self._model.__name__}",
                extra={"model": self._model.__name__, "id": id, "error": str(e)},
                exc_info=True,
            )
            raise DatabaseError(f"Failed to delete {self._model.__name__}: {e!s}")

    # 兼容旧版接口
    def remove(self, db: Session, id: Any) -> ModelType | None:
        """
        删除记录（兼容旧版接口，返回被删除的对象或None）
        """
        try:
            obj = self.get(db, id)
            if obj:
                db.delete(obj)
                db.commit()
                logger.info(
                    f"{self._model.__name__} deleted",
                    extra={"model": self._model.__name__, "id": id},
                )
            return obj
        except Exception as e:
            db.rollback()
            logger.error(
                f"Failed to delete {self._model.__name__}",
                extra={"model": self._model.__name__, "id": id, "error": str(e)},
                exc_info=True,
            )
            raise DatabaseError(f"Failed to delete {self._model.__name__}: {e!s}")

    def bulk_create(
        self, db: Session, objs_in: list[CreateSchemaType | dict[str, Any]]
    ) -> list[ModelType]:
        """批量创建"""
        try:
            db_objs = []
            for obj_in in objs_in:
                if isinstance(obj_in, BaseModel):
                    data = obj_in.model_dump(exclude_unset=True)
                else:
                    data = obj_in
                db_objs.append(self._model(**data))

            db.add_all(db_objs)
            db.commit()

            for db_obj in db_objs:
                db.refresh(db_obj)

            logger.info(
                f"Bulk created {len(db_objs)} {self._model.__name__} records",
                extra={"model": self._model.__name__, "count": len(db_objs)},
            )

            return db_objs

        except Exception as e:
            db.rollback()
            logger.error(
                f"Failed to bulk create {self._model.__name__}",
                extra={"model": self._model.__name__, "error": str(e)},
                exc_info=True,
            )
            raise DatabaseError(f"Failed to bulk create: {e!s}")

    def bulk_delete(self, db: Session, ids: list[Any]) -> int:
        """批量删除"""
        try:
            count = (
                db.query(self._model)
                .filter(self._model.id.in_(ids))
                .delete(synchronize_session=False)
            )
            db.commit()

            logger.info(
                f"Bulk deleted {count} {self._model.__name__} records",
                extra={"model": self._model.__name__, "count": count},
            )

            return count

        except Exception as e:
            db.rollback()
            logger.error(
                f"Failed to bulk delete {self._model.__name__}",
                extra={"model": self._model.__name__, "error": str(e)},
                exc_info=True,
            )
            raise DatabaseError(f"Failed to bulk delete: {e!s}")

    # ========== 查询构建器 ==========

    def query(self, db: Session) -> QueryBuilder[ModelType]:
        """获取查询构建器"""
        return QueryBuilder(self._model, db.query(self._model), self)

    # ========== 内部方法 ==========

    def _check_uniqueness(self, db: Session, data: dict[str, Any], exclude_id: Any | None = None):
        """检查唯一性约束"""
        for field in self._unique_fields:
            if field not in data or data[field] is None:
                continue

            query = db.query(self._model).filter(getattr(self._model, field) == data[field])

            if exclude_id is not None:
                query = query.filter(self._model.id != exclude_id)

            if query.first():
                raise ConflictError(f"Duplicate value for {field}: '{data[field]}'")


def get_repository(
    model_class: type[ModelType], db: Session = Depends(get_db)
) -> BaseRepository[ModelType, Any, Any]:
    """
    获取 Repository 实例的依赖函数

    Usage:
        @router.get("/items")
        def get_items(repo: BaseRepository[Item, Any, Any] = Depends(get_repository(Item))):
            return repo.get_multi(db)
    """
    return BaseRepository(model_class)


def create_repository_class(
    model_class: type[ModelType],
    search_fields: list[str] | None = None,
    unique_fields: list[str] | None = None,
) -> type[BaseRepository[ModelType, Any, Any]]:
    """
    动态创建 Repository 类

    Usage:
        SysAdminRepo = create_repository_class(
            SysAdmin,
            search_fields=['username', 'email'],
            unique_fields=['username', 'mobile', 'email']
        )
        repo = SysAdminRepo()
    """
    class_name = f"{model_class.__name__}Repository"

    attrs = {
        "DEFAULT_SEARCH_FIELDS": search_fields or [],
        "DEFAULT_UNIQUE_FIELDS": unique_fields or [],
    }

    return type(class_name, (BaseRepository,), attrs)
