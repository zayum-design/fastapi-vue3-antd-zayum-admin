"""
异步 Service 层基类
提供异步业务逻辑处理的基础功能
"""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import BusinessException
from app.repositories.async_base import AsyncBaseRepository

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class AsyncServiceError(BusinessException):
    """异步 Service 层错误"""

    pass


class AsyncBaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    异步 Service 层基类

    提供标准化的异步业务逻辑处理
    """

    def __init__(
        self, repository: AsyncBaseRepository[ModelType, CreateSchemaType, UpdateSchemaType]
    ):
        self._repo = repository

    # ========== 基础 CRUD 委托给 Repository ==========

    async def get(self, db: AsyncSession, id: Any) -> ModelType | None:
        """通过 ID 获取"""
        return await self._repo.get(db, id)

    async def get_or_404(self, db: AsyncSession, id: Any) -> ModelType:
        """通过 ID 获取，不存在则抛出异常"""
        return await self._repo.get_or_404(db, id)

    async def get_by(self, db: AsyncSession, **kwargs) -> ModelType | None:
        """通过字段获取"""
        return await self._repo.get_by(db, **kwargs)

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
        return await self._repo.get_multi(
            db, skip=skip, limit=limit, search=search, order_by=order_by
        )

    async def get_all(self, db: AsyncSession) -> list[ModelType]:
        """获取所有记录"""
        return await self._repo.get_all(db)

    async def count(self, db: AsyncSession) -> int:
        """获取记录数量"""
        return await self._repo.count(db)

    async def create(
        self, db: AsyncSession, obj_in: CreateSchemaType | dict[str, Any]
    ) -> ModelType:
        """创建记录"""
        return await self._repo.create(db, obj_in)

    async def update(
        self, db: AsyncSession, db_obj: ModelType, obj_in: UpdateSchemaType | dict[str, Any]
    ) -> ModelType:
        """更新记录"""
        return await self._repo.update(db, db_obj, obj_in)

    async def delete(self, db: AsyncSession, id: Any) -> ModelType | None:
        """删除记录"""
        return await self._repo.delete(db, id)

    async def exists(self, db: AsyncSession, id: Any) -> bool:
        """检查记录是否存在"""
        return await self._repo.exists(db, id)


class AsyncCrudService(AsyncBaseService[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    简化版异步 CRUD Service
    自动创建 Repository，适合简单的 CRUD 场景
    """

    def __init__(self, model_class: type[ModelType]):
        from app.repositories.async_base import AsyncBaseRepository

        repo = AsyncBaseRepository(model_class)
        super().__init__(repo)
