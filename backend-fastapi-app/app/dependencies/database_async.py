"""
异步数据库支持模块
基于 SQLAlchemy 2.0 的异步功能

使用说明：
1. 安装依赖: pip install asyncmy
2. 在需要异步数据库的路由中使用:

   from app.dependencies.database_async import get_async_db

   @router.get("/items")
   async def get_items(db: AsyncSession = Depends(get_async_db)):
       result = await db.execute(select(Item))
       return result.scalars().all()
"""

from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings
from app.utils.log_utils import logger

# 异步引擎
_async_engine: AsyncEngine | None = None
# 异步会话工厂
_AsyncSessionLocal: async_sessionmaker[AsyncSession] | None = None


class AsyncDatabaseError(Exception):
    """异步数据库错误"""

    pass


def get_async_engine() -> AsyncEngine:
    """
    获取或创建异步数据库引擎

    Returns:
        AsyncEngine: 异步数据库引擎
    """
    global _async_engine

    if _async_engine is None:
        try:
            _async_engine = create_async_engine(
                settings.ASYNC_DATABASE_URL,
                echo=settings.DEBUG,  # 调试模式下输出 SQL
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20,
                pool_recycle=1800,
                pool_timeout=30,
                connect_args={
                    "connect_timeout": 30,
                    "charset": "utf8mb4",
                },
            )
            logger.info("Async database engine created")
        except Exception as e:
            logger.error("Failed to create async database engine: {e}")
            raise AsyncDatabaseError(f"Database engine creation failed: {e}")

    return _async_engine


def get_async_session_factory() -> async_sessionmaker[AsyncSession]:
    """
    获取异步会话工厂

    Returns:
        async_sessionmaker: 异步会话工厂
    """
    global _AsyncSessionLocal

    if _AsyncSessionLocal is None:
        engine = get_async_engine()
        _AsyncSessionLocal = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )

    return _AsyncSessionLocal


async def check_async_db_connection() -> bool:
    """
    检查异步数据库连接

    Returns:
        bool: 连接是否成功
    """
    try:
        engine = get_async_engine()
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        logger.error("Async database connection check failed: {e}")
        return False


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    获取异步数据库会话的依赖函数

    Usage:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_async_db)):
            ...

    Yields:
        AsyncSession: 异步数据库会话
    """
    session_factory = get_async_session_factory()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            logger.error("Async database session error: {e}")
            raise
        finally:
            await session.close()


async def close_async_db():
    """关闭异步数据库连接"""
    global _async_engine, _AsyncSessionLocal

    if _async_engine:
        await _async_engine.dispose()
        _async_engine = None
        _AsyncSessionLocal = None
        logger.info("Async database engine disposed")


# ============== 异步 CRUD 基类 ==============

from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy import func, select

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

    async def get(self, db: AsyncSession, id: Any) -> ModelType | None:
        """通过 ID 获取"""
        result = await db.execute(select(self._model).where(self._model.id == id))
        return result.scalar_one_or_none()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> list[ModelType]:
        """获取多条记录"""
        result = await db.execute(select(self._model).offset(skip).limit(limit))
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
        if isinstance(obj_in, BaseModel):
            data = obj_in.model_dump(exclude_unset=True)
        else:
            data = obj_in

        db_obj = self._model(**data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)

        logger.info("Created {self._model.__name__}", extra={"id": getattr(db_obj, "id", None)})
        return db_obj

    async def update(
        self, db: AsyncSession, db_obj: ModelType, obj_in: UpdateSchemaType | dict[str, Any]
    ) -> ModelType:
        """更新记录"""
        if isinstance(obj_in, BaseModel):
            update_data = obj_in.model_dump(exclude_unset=True)
        else:
            update_data = obj_in

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)

        logger.info("Updated {self._model.__name__}", extra={"id": getattr(db_obj, "id", None)})
        return db_obj

    async def delete(self, db: AsyncSession, id: Any) -> ModelType | None:
        """删除记录"""
        obj = await self.get(db, id)
        if obj:
            await db.delete(obj)
            await db.commit()
            logger.info("Deleted {self._model.__name__}", extra={"id": id})
        return obj

    async def exists(self, db: AsyncSession, id: Any) -> bool:
        """检查记录是否存在"""
        result = await db.execute(select(self._model.id).where(self._model.id == id))
        return result.scalar() is not None


# ============== 使用示例 ==============

"""
# 创建异步 Repository 实例
sys_admin_async_repo = AsyncBaseRepository[SysAdmin, SysAdminCreate, SysAdminUpdate](SysAdmin)

# 在路由中使用
@router.get("/admins", response_model=List[SysAdminSchema])
async def list_admins(
    db: AsyncSession = Depends(get_async_db),
    skip: int = 0,
    limit: int = 100
):
    return await sys_admin_async_repo.get_multi(db, skip=skip, limit=limit)

@router.post("/admins", response_model=SysAdminSchema)
async def create_admin(
    admin_in: SysAdminCreate,
    db: AsyncSession = Depends(get_async_db)
):
    return await sys_admin_async_repo.create(db, admin_in)

@router.get("/admins/{admin_id}", response_model=SysAdminSchema)
async def get_admin(
    admin_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    admin = await sys_admin_async_repo.get(db, admin_id)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    return admin

@router.put("/admins/{admin_id}", response_model=SysAdminSchema)
async def update_admin(
    admin_id: int,
    admin_in: SysAdminUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    admin = await sys_admin_async_repo.get(db, admin_id)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    return await sys_admin_async_repo.update(db, admin, admin_in)

@router.delete("/admins/{admin_id}")
async def delete_admin(
    admin_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    admin = await sys_admin_async_repo.delete(db, admin_id)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    return {"message": "Admin deleted successfully"}
"""
