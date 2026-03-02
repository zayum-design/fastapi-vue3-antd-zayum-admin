"""
简化版 CRUD Router
大幅减少 API 层重复代码
"""

from collections.abc import Sequence
from typing import Any, Generic, TypeVar

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.repository import EnhancedRepository
from app.core.security import get_current_admin
from app.dependencies.database import get_db
from app.types.protocols import ModelProtocol
from app.utils.response_handlers import ErrorCode
from app.utils.responses import success_response

ModelType = TypeVar("ModelType", bound=ModelProtocol)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDRouter(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    通用 CRUD Router

    使用示例:
        router = CRUDRouter(
            prefix="/admin",
            tags=["admin"],
            repository=SysAdminRepository(),
            create_schema=SysAdminCreate,
            update_schema=SysAdminUpdate,
            resource_name="管理员"
        ).get_router()
    """

    def __init__(
        self,
        prefix: str,
        tags: Sequence[str],
        repository: EnhancedRepository[ModelType, CreateSchemaType, UpdateSchemaType],
        create_schema: type[CreateSchemaType],
        update_schema: type[UpdateSchemaType],
        resource_name: str = "资源",
        max_per_page: int = 200,
        dependencies: list[Any] | None = None,
    ):
        self.repository = repository
        self.create_schema = create_schema
        self.update_schema = update_schema
        self.resource_name = resource_name
        self.max_per_page = max_per_page

        deps = dependencies or [Depends(get_current_admin)]

        self.router = APIRouter(prefix=prefix, tags=list(tags), dependencies=deps)

        self._register_routes()

    def _register_routes(self):
        """注册标准 CRUD 路由"""
        self.router.add_api_route(
            "/list", self.list_items, methods=["GET"], summary=f"获取{self.resource_name}列表"
        )
        self.router.add_api_route(
            "/{item_id}", self.get_item, methods=["GET"], summary=f"获取{self.resource_name}详情"
        )
        self.router.add_api_route(
            "/create", self.create_item, methods=["POST"], summary=f"创建{self.resource_name}"
        )
        self.router.add_api_route(
            "/update/{item_id}",
            self.update_item,
            methods=["PUT"],
            summary=f"更新{self.resource_name}",
        )
        self.router.add_api_route(
            "/delete/{item_id}",
            self.delete_item,
            methods=["DELETE"],
            summary=f"删除{self.resource_name}",
        )

    def get_router(self) -> APIRouter:
        """获取配置好的 Router"""
        return self.router

    async def list_items(
        self,
        page: int = 1,
        per_page: int = 10,
        search: str | None = None,
        orderby: str | None = None,
        db: Session = Depends(get_db),
    ) -> dict[str, Any]:
        """
        获取列表

        Args:
            page: 页码，从1开始
            per_page: 每页数量，-1表示全部（最大200）
            search: 搜索关键词
            orderby: 排序规则，如 "created_at_desc", "name_asc"
        """
        if per_page == -1:
            per_page = self.max_per_page

        per_page = min(per_page, self.max_per_page)
        page = max(page, 1)

        items, total = self.repository.get_multi_with_total(
            db, page=page, per_page=per_page, search=search, orderby=orderby
        )

        return success_response(
            {
                "items": [item.to_dict() if hasattr(item, "to_dict") else item for item in items],
                "total": total,
                "page": page,
                "per_page": per_page,
            }
        )

    async def get_item(self, item_id: int, db: Session = Depends(get_db)) -> dict[str, Any]:
        """获取详情"""
        db_obj = self.repository.get(db, id=item_id)
        if db_obj is None:
            raise HTTPException(
                status_code=ErrorCode.NOT_FOUND.value, detail=f"{self.resource_name}不存在"
            )

        data = db_obj.to_dict() if hasattr(db_obj, "to_dict") else db_obj
        return success_response(data)

    async def create_item(
        self, obj_in: CreateSchemaType, db: Session = Depends(get_db)
    ) -> dict[str, Any]:
        """创建"""
        ret = self.repository.create(db, obj_in=obj_in)
        return success_response({"insert_id": getattr(ret, "id", None)})

    async def update_item(
        self, item_id: int, obj_in: UpdateSchemaType, db: Session = Depends(get_db)
    ) -> dict[str, Any]:
        """更新"""
        db_obj = self.repository.get(db, id=item_id)
        if not db_obj:
            raise HTTPException(
                status_code=ErrorCode.NOT_FOUND.value, detail=f"{self.resource_name}不存在"
            )

        updated_obj = self.repository.update(
            db, db_obj=db_obj, obj_in=obj_in.model_dump(exclude_unset=True)
        )

        data = updated_obj.to_dict() if hasattr(updated_obj, "to_dict") else updated_obj
        return success_response(data)

    async def delete_item(self, item_id: int, db: Session = Depends(get_db)) -> dict[str, Any]:
        """删除"""
        db_obj = self.repository.get(db, id=item_id)
        if db_obj is None:
            raise HTTPException(
                status_code=ErrorCode.NOT_FOUND.value, detail=f"{self.resource_name}不存在"
            )

        self.repository.remove(db, id=item_id)
        return success_response({})


class ReadOnlyRouter(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """只读 Router（仅包含 list 和 get）"""

    def __init__(
        self,
        prefix: str,
        tags: Sequence[str],
        repository: EnhancedRepository[ModelType, CreateSchemaType, UpdateSchemaType],
        resource_name: str = "资源",
        max_per_page: int = 200,
        dependencies: list[Any] | None = None,
    ):
        self.repository = repository
        self.resource_name = resource_name
        self.max_per_page = max_per_page

        deps = dependencies or [Depends(get_current_admin)]

        self.router = APIRouter(prefix=prefix, tags=list(tags), dependencies=deps)

        self._register_routes()

    def _register_routes(self):
        self.router.add_api_route(
            "/list", self.list_items, methods=["GET"], summary=f"获取{self.resource_name}列表"
        )
        self.router.add_api_route(
            "/{item_id}", self.get_item, methods=["GET"], summary=f"获取{self.resource_name}详情"
        )

    def get_router(self) -> APIRouter:
        return self.router

    async def list_items(
        self,
        page: int = 1,
        per_page: int = 10,
        search: str | None = None,
        orderby: str | None = None,
        db: Session = Depends(get_db),
    ) -> dict[str, Any]:
        if per_page == -1:
            per_page = self.max_per_page

        per_page = min(per_page, self.max_per_page)
        page = max(page, 1)

        items, total = self.repository.get_multi_with_total(
            db, page=page, per_page=per_page, search=search, orderby=orderby
        )

        return success_response(
            {
                "items": [item.to_dict() if hasattr(item, "to_dict") else item for item in items],
                "total": total,
                "page": page,
                "per_page": per_page,
            }
        )

    async def get_item(self, item_id: int, db: Session = Depends(get_db)) -> dict[str, Any]:
        db_obj = self.repository.get(db, id=item_id)
        if db_obj is None:
            raise HTTPException(
                status_code=ErrorCode.NOT_FOUND.value, detail=f"{self.resource_name}不存在"
            )

        data = db_obj.to_dict() if hasattr(db_obj, "to_dict") else db_obj
        return success_response(data)
