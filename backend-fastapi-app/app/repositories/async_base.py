"""
异步 Repository 基类
提供标准化的异步 CRUD 操作
"""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import DatabaseError, NotFoundError
from app.utils.log_utils import logger

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class AsyncBaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    异步通用 Repository 基类

    提供标准化的异步 CRUD 操作
    """

    def __init__(self, model: type[ModelType]):
        self._model = model
        self._searchable_fields: list[str] = []
        self._unique_fields: list[str] = []

    def set_searchable_fields(self, fields: list[str]) -> "AsyncBaseRepository":
        """设置可搜索字段"""
        self._searchable_fields = fields
        return self

    def set_unique_fields(self, fields: list[str]) -> "AsyncBaseRepository":
        """设置唯一字段"""
        self._unique_fields = fields
        return self

    # ========== 基础 CRUD ==========

    async def get(self, db: AsyncSession, id: Any) -> ModelType | None:
        """通过 ID 获取"""
        result = await db.execute(select(self._model).where(self._model.id == id))
        return result.scalar_one_or_none()

    async def get_or_404(self, db: AsyncSession, id: Any) -> ModelType:
        """通过 ID 获取，不存在则抛出异常"""
        obj = await self.get(db, id)
        if obj is None:
            raise NotFoundError(f"{self._model.__name__} with id={id} not found")
        return obj

    async def get_by(self, db: AsyncSession, **kwargs) -> ModelType | None:
        """通过字段获取"""
        query = select(self._model)
        for key, value in kwargs.items():
            if hasattr(self._model, key):
                query = query.where(getattr(self._model, key) == value)

        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
        order_by: str | None = None,
    ) -> list[ModelType]:
        """获取多条记录"""
        query = select(self._model)

        # 搜索
        if search and self._searchable_fields:
            search_pattern = f"%{search}%"
            filters = []
            for field_name in self._searchable_fields:
                if hasattr(self._model, field_name):
                    field = getattr(self._model, field_name)
                    filters.append(field.ilike(search_pattern))
            if filters:
                query = query.where(or_(*filters))

        # 排序
        if order_by:
            if order_by.startswith("-"):
                field_name = order_by[1:]
                if hasattr(self._model, field_name):
                    query = query.order_by(getattr(self._model, field_name).desc())
            else:
                if hasattr(self._model, order_by):
                    query = query.order_by(getattr(self._model, order_by).asc())

        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_all(self, db: AsyncSession) -> list[ModelType]:
        """获取所有记录"""
        result = await db.execute(select(self._model))
        return result.scalars().all()

    async def count(self, db: AsyncSession) -> int:
        """获取记录数量"""
        result = await db.execute(select(func.count()).select_from(self._model))
        return result.scalar()

    async def create(
        self, db: AsyncSession, obj_in: CreateSchemaType | dict[str, Any]
    ) -> ModelType:
        """创建记录"""
        try:
            # 转换为字典
            if isinstance(obj_in, BaseModel):
                data = obj_in.model_dump(exclude_unset=True)
            else:
                data = obj_in

            # 创建对象
            db_obj = self._model(**data)
            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)

            logger.info(
                f"{self._model.__name__} created", extra={"id": getattr(db_obj, "id", None)}
            )
            return db_obj

        except Exception as e:
            await db.rollback()
            logger.error(
                f"Failed to create {self._model.__name__}", extra={"error": str(e)}, exc_info=True
            )
            raise DatabaseError(f"Failed to create {self._model.__name__}: {e!s}")

    async def update(
        self, db: AsyncSession, db_obj: ModelType, obj_in: UpdateSchemaType | dict[str, Any]
    ) -> ModelType:
        """更新记录"""
        try:
            # 转换为字典
            if isinstance(obj_in, BaseModel):
                update_data = obj_in.model_dump(exclude_unset=True)
            else:
                update_data = obj_in

            # 更新字段
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)

            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)

            logger.info(
                f"{self._model.__name__} updated", extra={"id": getattr(db_obj, "id", None)}
            )
            return db_obj

        except Exception as e:
            await db.rollback()
            logger.error(
                f"Failed to update {self._model.__name__}",
                extra={"id": getattr(db_obj, "id", None), "error": str(e)},
                exc_info=True,
            )
            raise DatabaseError(f"Failed to update {self._model.__name__}: {e!s}")

    async def delete(self, db: AsyncSession, id: Any) -> ModelType | None:
        """删除记录"""
        try:
            obj = await self.get(db, id)
            if obj:
                await db.delete(obj)
                await db.commit()
                logger.info("{self._model.__name__} deleted", extra={"id": id})
            return obj

        except Exception as e:
            await db.rollback()
            logger.error(
                f"Failed to delete {self._model.__name__}",
                extra={"id": id, "error": str(e)},
                exc_info=True,
            )
            raise DatabaseError(f"Failed to delete {self._model.__name__}: {e!s}")

    async def exists(self, db: AsyncSession, id: Any) -> bool:
        """检查记录是否存在"""
        result = await db.execute(select(self._model.id).where(self._model.id == id))
        return result.scalar() is not None
