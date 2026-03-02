"""
CRUD代码生成器
生成数据库操作代码
"""

from sqlalchemy import Table


class CrudGenerator:
    """CRUD代码生成器类"""
    
    def generate(self, inspector, table: Table) -> str:
        """生成CRUD代码"""
        class_name = "".join(word.capitalize() for word in table.name.split("_"))
        table_name = table.name
        
        # 获取主键列
        primary_key_columns = [col.name for col in table.primary_key.columns]
        primary_key = primary_key_columns[0] if primary_key_columns else "id"
        
        # 获取所有列名
        all_columns = [col.name for col in table.columns]
        
        # 构建CRUD代码
        crud_code = f'''"""
{table_name} 表的CRUD操作
"""

from typing import List, Optional, Dict, Any, Union, TYPE_CHECKING
from fastapi_babel import _
from sqlalchemy.orm import Session, Query
from sqlalchemy import and_, or_
from app.modules.admin.{table_name}.models.{table_name} import {class_name}
from app.modules.admin.{table_name}.schemas.{table_name} import {class_name}Create, {class_name}Update
from app.utils.log_utils import logger


class CRUD{class_name}:
    """{class_name} CRUD操作类"""
    
    SEARCHABLE_FIELDS = {all_columns}

    def get(self, db: Session, {primary_key}: int) -> Optional[{class_name}]:
        """Get {class_name} by ID"""
        return db.get({class_name}, {primary_key})

    def _apply_search_filter(self, query: Query, search: Optional[str]) -> Query:
        """Apply search filter"""
        if not search or not self.SEARCHABLE_FIELDS:
            return query
        
        search_pattern = f"%{{search}}%"
        filters = []
        for field in self.SEARCHABLE_FIELDS:
            if hasattr({class_name}, field):
                filters.append(getattr({class_name}, field).ilike(search_pattern))
        if not filters:
             return query
        return query.filter(or_(*filters))

    def _apply_order_by(self, query: Query, orderby: Optional[str]) -> Query:
        """Apply ordering"""
        if not orderby:
            return query
        
        try:
            field, direction = orderby.rsplit("_", 1)
            if not hasattr({class_name}, field):
                logger.error(_("Invalid sort field: {{field}} for model {class_name}"))
                return query
            order_column = getattr({class_name}, field)
            if direction.lower() == "asc":
                return query.order_by(order_column.asc())
            elif direction.lower() == "desc":
                return query.order_by(order_column.desc())
            logger.warning(_("Invalid sort direction: {{direction}} for field {{field}}"))
            return query
        except ValueError:
            logger.error(_("Invalid orderby format. Expected format: field_direction"))
            return query
        except AttributeError:
            logger.error(_("Sort field does not exist on model {class_name}"))
            return query

    def filter(self, db: Session, *criterion) -> 'QueryBuilder{class_name}':
        """
        Apply custom SQLAlchemy filter criteria and return a QueryBuilder instance.
        """
        initial_query = db.query({class_name})
        if criterion:
            initial_query = initial_query.filter(*criterion)
        return QueryBuilder{class_name}(db=db, query=initial_query, crud_base=self)

    def get_multi(
        self, 
        db: Session, 
        page: int = 1, 
        per_page: int = 10, 
        search: Optional[str] = None, 
        orderby: Optional[str] = None,
        base_query: Optional[Query] = None
    ) -> List[{class_name}]:
        """Get paginated list of {class_name} records"""
        page = max(1, page)
        per_page = max(1, min(per_page, 100))
        
        query = base_query if base_query is not None else db.query({class_name})
        query = self._apply_search_filter(query, search)
        query = self._apply_order_by(query, orderby)
        
        return query.offset((page - 1) * per_page).limit(per_page).all()

    def get_all(
        self, 
        db: Session, 
        search: Optional[str] = None, 
        orderby: Optional[str] = None,
        base_query: Optional[Query] = None
    ) -> List[{class_name}]:
        """Get all {class_name} records"""
        query = base_query if base_query is not None else db.query({class_name})
        query = self._apply_search_filter(query, search)
        query = self._apply_order_by(query, orderby)
        return query.all()

    def get_total(self, db: Session, search: Optional[str] = None, base_query: Optional[Query] = None) -> int:
        """Get total count of {class_name} records"""
        query = base_query if base_query is not None else db.query({class_name})
        query = self._apply_search_filter(query, search)
        return query.count()

    def create(self, db: Session, obj_in: {class_name}Create) -> {class_name}:
        """Create new {class_name} record"""
        try:
            db_obj = {class_name}(**obj_in.model_dump(exclude_unset=True))
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except Exception:
            db.rollback()
            logger.error("Failed to create {class_name}", exc_info=True)
            raise

    def update(
        self, 
        db: Session, 
        db_obj: {class_name}, 
        obj_in: Union[Dict[str, Any], {class_name}Update]
    ) -> {class_name}:
        """Update existing {class_name} record"""
        try:
            update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except Exception:
            db.rollback()
            logger.error("Failed to update {class_name} ({{db_obj.{primary_key}}})", exc_info=True)
            raise

    def remove(self, db: Session, {primary_key}: int) -> Optional[{class_name}]:
        """Delete {class_name} by ID"""
        try:
            obj = self.get(db, {primary_key})
            if obj:
                db.delete(obj)
                db.commit()
            return obj
        except Exception:
            db.rollback()
            logger.error("Failed to delete {class_name} (ID: {{{primary_key}}})", exc_info=True)
            raise


class QueryBuilder{class_name}:
    def __init__(self, db: Session, query: Query, crud_base: CRUD{class_name}):
        self._db: Session = db
        self._query: Query = query
        self._crud_base: CRUD{class_name} = crud_base

    def filter(self, *criterion) -> 'QueryBuilder{class_name}':
        """Apply additional filter criteria to the current query."""
        if criterion:
            self._query = self._query.filter(*criterion)
        return self

    def _get_effective_db(self, db_param: Optional[Session]) -> Session:
        """Determine the actual database session to use."""
        if db_param is not None and db_param is not self._db:
            logger.warning(
                "QueryBuilder method called with a DB session different from its initial one. "
                "The initial session will be used for the query execution."
            )
        return self._db

    def get_all(self, db: Optional[Session] = None, search: Optional[str] = None, orderby: Optional[str] = None) -> List[{class_name}]:
        """Execute the query and return all results."""
        effective_db = self._get_effective_db(db)
        return self._crud_base.get_all(db=effective_db, search=search, orderby=orderby, base_query=self._query)

    def get_multi(
        self, 
        db: Optional[Session] = None,
        page: int = 1, 
        per_page: int = 10, 
        search: Optional[str] = None, 
        orderby: Optional[str] = None
    ) -> List[{class_name}]:
        """Execute the query with pagination."""
        effective_db = self._get_effective_db(db)
        return self._crud_base.get_multi(
            db=effective_db, 
            page=page, 
            per_page=per_page, 
            search=search, 
            orderby=orderby, 
            base_query=self._query
        )

    def get_total(self, db: Optional[Session] = None, search: Optional[str] = None) -> int:
        """Execute the query to get the total count of records."""
        effective_db = self._get_effective_db(db)
        return self._crud_base.get_total(db=effective_db, search=search, base_query=self._query)

    def all(self) -> List[{class_name}]:
        """Directly execute .all() on the current query object."""
        return self._query.all()

    def first(self) -> Optional[{class_name}]:
        """Directly execute .first() on the current query object."""
        return self._query.first()

    def count(self) -> int:
        """Directly execute .count() on the current query object."""
        return self._query.count()


crud_{table_name} = CRUD{class_name}()
'''
        return crud_code
