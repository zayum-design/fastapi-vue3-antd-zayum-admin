from typing import Optional, Type, TypeVar, Generic, List, Sequence
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.dependencies.database import get_db
from app.core.security import get_current_admin
from app.utils.responses import success_response
from app.utils.response_handlers import ErrorCode

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDRouter(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """通用CRUD路由器基类，减少代码重复"""

    def __init__(
        self,
        prefix: str,
        tags: Sequence[str],
        crud_class: any,
        model: Type[ModelType],
        create_schema: Type[CreateSchemaType],
        update_schema: Type[UpdateSchemaType],
        resource_name: str,
        max_per_page: int = 200
    ):
        self.router = APIRouter(
            prefix=prefix,
            tags=list(tags),
            dependencies=[Depends(get_current_admin)]
        )
        self.crud = crud_class
        self.model = model
        self.create_schema = create_schema
        self.update_schema = update_schema
        self.resource_name = resource_name
        self.max_per_page = max_per_page
        self._register_routes()

    def _register_routes(self):
        """注册标准的CRUD路由"""
        self.router.add_api_route(
            "/list",
            self.list_items,
            methods=["GET"]
        )
        self.router.add_api_route(
            "/{id}",
            self.get_item,
            methods=["GET"]
        )
        self.router.add_api_route(
            "/create",
            self.create_item,
            methods=["POST"]
        )
        self.router.add_api_route(
            "/update/{id}",
            self.update_item,
            methods=["PUT"]
        )
        self.router.add_api_route(
            "/delete/{id}",
            self.delete_item,
            methods=["DELETE"]
        )

    def list_items(
        self,
        page: int = 1,
        per_page: int = 10,
        search: Optional[str] = None,
        orderby: Optional[str] = None,
        db: Session = Depends(get_db)
    ):
        if per_page == -1:
            per_page = self.max_per_page
        
        per_page = min(per_page, self.max_per_page)
        page = max(page, 1)
        
        items = self.crud.get_multi(db, page=page, per_page=per_page, search=search, orderby=orderby)
        total = self.crud.get_total(db, search=search)
        
        return success_response({
            "items": [item.to_dict() for item in items],
            "total": total,
            "page": page,
            "per_page": per_page,
        })

    def get_item(self, id: int, db: Session = Depends(get_db)):
        db_obj = self.crud.get(db, id=id)
        if db_obj is None:
            raise HTTPException(
                status_code=ErrorCode.NOT_FOUND.value,
                detail=f"{self.resource_name} not found."
            )
        return success_response(db_obj.to_dict())

    def create_item(self, obj_in: CreateSchemaType, db: Session = Depends(get_db)):
        ret = self.crud.create(db, obj_in=obj_in)
        return success_response({"insert_id": ret.id})

    def update_item(self, id: int, obj_in: UpdateSchemaType, db: Session = Depends(get_db)):
        db_obj = self.crud.get(db, id=id)
        if not db_obj:
            raise HTTPException(
                status_code=ErrorCode.NOT_FOUND.value,
                detail=f"{self.resource_name} not found."
            )
        updated_obj = self.crud.update(
            db, db_obj=db_obj, obj_in=obj_in.model_dump(exclude_unset=True)
        )
        return success_response(updated_obj.to_dict())

    def delete_item(self, id: int, db: Session = Depends(get_db)):
        db_obj = self.crud.get(db, id=id)
        if db_obj is None:
            raise HTTPException(
                status_code=ErrorCode.NOT_FOUND.value,
                detail=f"{self.resource_name} not found."
            )
        self.crud.remove(db, id=id)
        return success_response({})
