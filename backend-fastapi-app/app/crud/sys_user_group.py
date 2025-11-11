from typing import List, Optional, Dict, Any, Union, TYPE_CHECKING
from fastapi_babel import _
from sqlalchemy.orm import Session, Query
from sqlalchemy import and_, or_
from app.models.sys_user_group import SysUserGroup
from app.schemas.sys_user_group import SysUserGroupCreate, SysUserGroupUpdate
from app.utils.log_utils import logger

# Forward declaration for QueryBuilder to avoid circular import issues
if TYPE_CHECKING:
    class _QueryBuilderSysUserGroup:
        pass

class CRUDSysUserGroup:
    SEARCHABLE_FIELDS = ['name', 'status']

    def get(self, db: Session, id: int) -> Optional[SysUserGroup]:
        """Get SysUserGroup by ID"""
        return db.get(SysUserGroup,id)

    def _apply_search_filter(self, query: Query, search: Optional[str]) -> Query:
        """Apply search filter"""
        if not search or not self.SEARCHABLE_FIELDS:
            return query
        
        search_pattern = f"%{search}%"
        filters = []
        for field in self.SEARCHABLE_FIELDS:
            if hasattr(SysUserGroup, field):
                filters.append(getattr(SysUserGroup, field).ilike(search_pattern))
        if not filters:
             return query
        return query.filter(or_(*filters))

    def _apply_order_by(self, query: Query, orderby: Optional[str]) -> Query:
        """Apply ordering"""
        if not orderby:
            return query
        
        try:
            field, direction = orderby.rsplit("_", 1)
            if not hasattr(SysUserGroup, field):
                logger.error(_(f"Invalid sort field: {field} for model SysUserGroup"))
                return query
            order_column = getattr(SysUserGroup, field)
            if direction.lower() == "asc":
                return query.order_by(order_column.asc())
            elif direction.lower() == "desc":
                return query.order_by(order_column.desc())
            logger.warning(_(f"Invalid sort direction: {direction} for field {field}"))
            return query
        except ValueError: # Handles rsplit error if '_' not found
            logger.error(_("Invalid orderby format. Expected format: field_direction"))
            return query
        except AttributeError: # Should be caught by hasattr check, but as a fallbacky
            logger.error(_(f"Sort field does not exist on model SysUserGroup"))
            return query

    def filter(self, db: Session, *criterion) -> 'QueryBuilderSysUserGroup':
        """
        Apply custom SQLAlchemy filter criteria and return a QueryBuilder instance.
        Allows for chainable calls like .get_all(), .get_multi(), etc.
        Args:
            db (Session): SQLAlchemy database session.
            *criterion: One or more SQLAlchemy filter expressions
                        (e.g., SysUserGroup.name == "example", SysUserGroup.status == 1).
        """
        initial_query = db.query(SysUserGroup)
        if criterion:
            initial_query = initial_query.filter(*criterion)
        return QueryBuilderSysUserGroup(db=db, query=initial_query, crud_base=self)

    def get_multi(
        self, 
        db: Session, 
        page: int = 1, 
        per_page: int = 10, 
        search: Optional[str] = None, 
        orderby: Optional[str] = None,
        base_query: Optional[Query] = None
    ) -> List[SysUserGroup]:
        """Get paginated list of SysUserGroup records"""
        page = max(1, page)
        per_page = max(1, min(per_page, 100))
        
        query = base_query if base_query is not None else db.query(SysUserGroup)
        query = self._apply_search_filter(query, search)
        query = self._apply_order_by(query, orderby)
        
        return query.offset((page - 1) * per_page).limit(per_page).all()

    def get_all(
        self, 
        db: Session, 
        search: Optional[str] = None, 
        orderby: Optional[str] = None,
        base_query: Optional[Query] = None
    ) -> List[SysUserGroup]:
        """Get all SysUserGroup records"""
        query = base_query if base_query is not None else db.query(SysUserGroup)
        query = self._apply_search_filter(query, search)
        query = self._apply_order_by(query, orderby)
        return query.all()

    def get_total(self, db: Session, search: Optional[str] = None, base_query: Optional[Query] = None) -> int:
        """Get total count of SysUserGroup records"""
        query = base_query if base_query is not None else db.query(SysUserGroup)
        query = self._apply_search_filter(query, search)
        # Order by is not needed for count
        return query.count()

    def create(self, db: Session, obj_in: SysUserGroupCreate) -> SysUserGroup:
        """Create new SysUserGroup record with uniqueness validation"""
        try:
            # Check name uniqueness
            if hasattr(obj_in, 'name') and getattr(obj_in, 'name') is not None:
                existing = db.query(SysUserGroup).filter(
                    SysUserGroup.name == getattr(obj_in, 'name')
                ).first()
                if existing:
                    raise ValueError(_(f"Duplicate value for name: '{getattr(obj_in, 'name')}'"))

            db_obj = SysUserGroup(**obj_in.model_dump(exclude_unset=True))
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except Exception:
            db.rollback()
            logger.error(f"Failed to create SysUserGroup", exc_info=True)
            raise

    def update(
        self, 
        db: Session, 
        db_obj: SysUserGroup, 
        obj_in: Union[Dict[str, Any], SysUserGroupUpdate]
    ) -> SysUserGroup:
        """Update existing SysUserGroup record with uniqueness validation"""
        try:
            update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
            # Check name uniqueness if being changed
            if 'name' in update_data and update_data['name'] is not None:
                new_name = update_data['name']
                if new_name != getattr(db_obj, 'name'):
                    existing = db.query(SysUserGroup).filter(
                        SysUserGroup.name == new_name,
                        SysUserGroup.id != getattr(db_obj, 'id')
                    ).first()
                    if existing:
                        raise ValueError(_(f"Duplicate value for name: '{new_name}'"))

            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except Exception:
            db.rollback()
            logger.error(f"Failed to update SysUserGroup ({db_obj.id})", exc_info=True)
            raise

    def remove(self, db: Session, id: int) -> Optional[SysUserGroup]:
        """Delete SysUserGroup by ID"""
        try:
            obj = self.get(db, id) # Use self.get for consistency
            if obj:
                db.delete(obj)
                db.commit()
            return obj
        except Exception:
            db.rollback()
            logger.error(f"Failed to delete SysUserGroup (ID: {id})", exc_info=True)
            raise


# Helper class for chainable query building
class QueryBuilderSysUserGroup:
    def __init__(self, db: Session, query: Query, crud_base: CRUDSysUserGroup):
        self._db: Session = db
        self._query: Query = query
        self._crud_base: CRUDSysUserGroup = crud_base

    def filter(self, *criterion) -> 'QueryBuilderSysUserGroup':
        """Apply additional filter criteria to the current query."""
        if criterion:
            self._query = self._query.filter(*criterion)
        return self

    def _get_effective_db(self, db_param: Optional[Session]) -> Session:
        """Determine the actual database session to use. Prefers the initial session."""
        if db_param is not None and db_param is not self._db:
            logger.warning(
                "QueryBuilder method called with a DB session different from its initial one. "
                "The initial session will be used for the query execution."
            )
        return self._db

    def get_all(self, db: Optional[Session] = None, search: Optional[str] = None, orderby: Optional[str] = None) -> List[SysUserGroup]:
        """Execute the query and return all results, applying optional search and ordering."""
        effective_db = self._get_effective_db(db)
        return self._crud_base.get_all(db=effective_db, search=search, orderby=orderby, base_query=self._query)

    def get_multi(
        self, 
        db: Optional[Session] = None,
        page: int = 1, 
        per_page: int = 10, 
        search: Optional[str] = None, 
        orderby: Optional[str] = None
    ) -> List[SysUserGroup]:
        """Execute the query with pagination, applying optional search and ordering."""
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
        """Execute the query to get the total count of records, applying optional search."""
        effective_db = self._get_effective_db(db)
        return self._crud_base.get_total(db=effective_db, search=search, base_query=self._query)

    def all(self) -> List[SysUserGroup]:
        """Directly execute .all() on the current query object."""
        return self._query.all()

    def first(self) -> Optional[SysUserGroup]:
        """Directly execute .first() on the current query object."""
        return self._query.first()

    def count(self) -> int:
        """Directly execute .count() on the current query object."""
        return self._query.count()


crud_sys_user_group = CRUDSysUserGroup()
