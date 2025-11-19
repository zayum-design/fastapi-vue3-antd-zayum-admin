from typing import List, Optional, Dict, Any, Union, TYPE_CHECKING
from fastapi_babel import _
from sqlalchemy.orm import Session, Query
from sqlalchemy import and_, or_
from app.models.sys_analytics_summary import SysAnalyticsSummary
from app.schemas.sys_analytics_summary import SysAnalyticsSummaryCreate, SysAnalyticsSummaryUpdate
from app.utils.log_utils import logger

# Forward declaration for QueryBuilder to avoid circular import issues
if TYPE_CHECKING:
    class _QueryBuilderSysAnalyticsSummary:
        pass

class CRUDSysAnalyticsSummary:
    SEARCHABLE_FIELDS = ['summary_type', 'region_name']

    def get(self, db: Session, id: int) -> Optional[SysAnalyticsSummary]:
        """Get SysAnalyticsSummary by ID"""
        return db.get(SysAnalyticsSummary,id)

    def _apply_search_filter(self, query: Query, search: Optional[str]) -> Query:
        """Apply search filter"""
        if not search or not self.SEARCHABLE_FIELDS:
            return query
        
        search_pattern = f"%{search}%"
        filters = []
        for field in self.SEARCHABLE_FIELDS:
            if hasattr(SysAnalyticsSummary, field):
                filters.append(getattr(SysAnalyticsSummary, field).ilike(search_pattern))
        if not filters:
             return query
        return query.filter(or_(*filters))

    def _apply_order_by(self, query: Query, orderby: Optional[str]) -> Query:
        """Apply ordering"""
        if not orderby:
            return query
        
        try:
            field, direction = orderby.rsplit("_", 1)
            if not hasattr(SysAnalyticsSummary, field):
                logger.error(_(f"Invalid sort field: {field} for model SysAnalyticsSummary"))
                return query
            order_column = getattr(SysAnalyticsSummary, field)
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
            logger.error(_(f"Sort field does not exist on model SysAnalyticsSummary"))
            return query

    def filter(self, db: Session, *criterion) -> 'QueryBuilderSysAnalyticsSummary':
        """
        Apply custom SQLAlchemy filter criteria and return a QueryBuilder instance.
        Allows for chainable calls like .get_all(), .get_multi(), etc.
        Args:
            db (Session): SQLAlchemy database session.
            *criterion: One or more SQLAlchemy filter expressions
                        (e.g., SysAnalyticsSummary.name == "example", SysAnalyticsSummary.status == 1).
        """
        initial_query = db.query(SysAnalyticsSummary)
        if criterion:
            initial_query = initial_query.filter(*criterion)
        return QueryBuilderSysAnalyticsSummary(db=db, query=initial_query, crud_base=self)

    def get_multi(
        self, 
        db: Session, 
        page: int = 1, 
        per_page: int = 10, 
        search: Optional[str] = None, 
        orderby: Optional[str] = None,
        base_query: Optional[Query] = None
    ) -> List[SysAnalyticsSummary]:
        """Get paginated list of SysAnalyticsSummary records"""
        page = max(1, page)
        per_page = max(1, min(per_page, 100))
        
        query = base_query if base_query is not None else db.query(SysAnalyticsSummary)
        query = self._apply_search_filter(query, search)
        query = self._apply_order_by(query, orderby)
        
        return query.offset((page - 1) * per_page).limit(per_page).all()

    def get_all(
        self, 
        db: Session, 
        search: Optional[str] = None, 
        orderby: Optional[str] = None,
        base_query: Optional[Query] = None
    ) -> List[SysAnalyticsSummary]:
        """Get all SysAnalyticsSummary records"""
        query = base_query if base_query is not None else db.query(SysAnalyticsSummary)
        query = self._apply_search_filter(query, search)
        query = self._apply_order_by(query, orderby)
        return query.all()

    def get_total(self, db: Session, search: Optional[str] = None, base_query: Optional[Query] = None) -> int:
        """Get total count of SysAnalyticsSummary records"""
        query = base_query if base_query is not None else db.query(SysAnalyticsSummary)
        query = self._apply_search_filter(query, search)
        # Order by is not needed for count
        return query.count()

    def create(self, db: Session, obj_in: SysAnalyticsSummaryCreate) -> SysAnalyticsSummary:
        """Create new SysAnalyticsSummary record with uniqueness validation"""
        try:
            # Check composite uniqueness constraint 1 (fields: summary_type, summary_date)
            filters = []
            all_fields_present = True
            if hasattr(obj_in, 'summary_type') and getattr(obj_in, 'summary_type') is not None:
                filters.append(SysAnalyticsSummary.summary_type == getattr(obj_in, 'summary_type'))
            else:
                all_fields_present = False # If any part of composite key is None, skip check or handle as per policy
                # Depending on DB, NULLs might not be considered equal for unique constraints.
                # For now, if any part is None, we assume it won't cause a unique violation by itself.
                # If your DB treats NULLs as equal in unique constraints, this logic needs adjustment.
                # Skip this constraint check if any field is None
                continue_check = False
            if hasattr(obj_in, 'summary_date') and getattr(obj_in, 'summary_date') is not None:
                filters.append(SysAnalyticsSummary.summary_date == getattr(obj_in, 'summary_date'))
            else:
                all_fields_present = False # If any part of composite key is None, skip check or handle as per policy
                # Depending on DB, NULLs might not be considered equal for unique constraints.
                # For now, if any part is None, we assume it won't cause a unique violation by itself.
                # If your DB treats NULLs as equal in unique constraints, this logic needs adjustment.
                # Skip this constraint check if any field is None
                continue_check = False
            if all_fields_present and len(filters) == 2:
                existing = db.query(SysAnalyticsSummary).filter(and_(*filters)).first()
                if existing:
                    values_str = ', '.join([f"{getattr(obj_in, c)}" for c in ['summary_type', 'summary_date']])
                    raise ValueError(_(f"Duplicate combination of values for fields: summary_type, summary_date. Values: [{values_str}]"))

            # Check composite uniqueness constraint 2 (fields: summary_type, summary_year, summary_month)
            filters = []
            all_fields_present = True
            if hasattr(obj_in, 'summary_type') and getattr(obj_in, 'summary_type') is not None:
                filters.append(SysAnalyticsSummary.summary_type == getattr(obj_in, 'summary_type'))
            else:
                all_fields_present = False # If any part of composite key is None, skip check or handle as per policy
                # Depending on DB, NULLs might not be considered equal for unique constraints.
                # For now, if any part is None, we assume it won't cause a unique violation by itself.
                # If your DB treats NULLs as equal in unique constraints, this logic needs adjustment.
                # Skip this constraint check if any field is None
                continue_check = False
            if hasattr(obj_in, 'summary_year') and getattr(obj_in, 'summary_year') is not None:
                filters.append(SysAnalyticsSummary.summary_year == getattr(obj_in, 'summary_year'))
            else:
                all_fields_present = False # If any part of composite key is None, skip check or handle as per policy
                # Depending on DB, NULLs might not be considered equal for unique constraints.
                # For now, if any part is None, we assume it won't cause a unique violation by itself.
                # If your DB treats NULLs as equal in unique constraints, this logic needs adjustment.
                # Skip this constraint check if any field is None
                continue_check = False
            if hasattr(obj_in, 'summary_month') and getattr(obj_in, 'summary_month') is not None:
                filters.append(SysAnalyticsSummary.summary_month == getattr(obj_in, 'summary_month'))
            else:
                all_fields_present = False # If any part of composite key is None, skip check or handle as per policy
                # Depending on DB, NULLs might not be considered equal for unique constraints.
                # For now, if any part is None, we assume it won't cause a unique violation by itself.
                # If your DB treats NULLs as equal in unique constraints, this logic needs adjustment.
                # Skip this constraint check if any field is None
                continue_check = False
            if all_fields_present and len(filters) == 3:
                existing = db.query(SysAnalyticsSummary).filter(and_(*filters)).first()
                if existing:
                    values_str = ', '.join([f"{getattr(obj_in, c)}" for c in ['summary_type', 'summary_year', 'summary_month']])
                    raise ValueError(_(f"Duplicate combination of values for fields: summary_type, summary_year, summary_month. Values: [{values_str}]"))

            # Check composite uniqueness constraint 3 (fields: summary_type, region_name)
            filters = []
            all_fields_present = True
            if hasattr(obj_in, 'summary_type') and getattr(obj_in, 'summary_type') is not None:
                filters.append(SysAnalyticsSummary.summary_type == getattr(obj_in, 'summary_type'))
            else:
                all_fields_present = False # If any part of composite key is None, skip check or handle as per policy
                # Depending on DB, NULLs might not be considered equal for unique constraints.
                # For now, if any part is None, we assume it won't cause a unique violation by itself.
                # If your DB treats NULLs as equal in unique constraints, this logic needs adjustment.
                # Skip this constraint check if any field is None
                continue_check = False
            if hasattr(obj_in, 'region_name') and getattr(obj_in, 'region_name') is not None:
                filters.append(SysAnalyticsSummary.region_name == getattr(obj_in, 'region_name'))
            else:
                all_fields_present = False # If any part of composite key is None, skip check or handle as per policy
                # Depending on DB, NULLs might not be considered equal for unique constraints.
                # For now, if any part is None, we assume it won't cause a unique violation by itself.
                # If your DB treats NULLs as equal in unique constraints, this logic needs adjustment.
                # Skip this constraint check if any field is None
                continue_check = False
            if all_fields_present and len(filters) == 2:
                existing = db.query(SysAnalyticsSummary).filter(and_(*filters)).first()
                if existing:
                    values_str = ', '.join([f"{getattr(obj_in, c)}" for c in ['summary_type', 'region_name']])
                    raise ValueError(_(f"Duplicate combination of values for fields: summary_type, region_name. Values: [{values_str}]"))

            db_obj = SysAnalyticsSummary(**obj_in.model_dump(exclude_unset=True))
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except Exception:
            db.rollback()
            logger.error(f"Failed to create SysAnalyticsSummary", exc_info=True)
            raise

    def update(
        self, 
        db: Session, 
        db_obj: SysAnalyticsSummary, 
        obj_in: Union[Dict[str, Any], SysAnalyticsSummaryUpdate]
    ) -> SysAnalyticsSummary:
        """Update existing SysAnalyticsSummary record with uniqueness validation"""
        try:
            update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
            # Check composite uniqueness constraint 1 (fields: summary_type, summary_date)
            # This check is complex: only validate if all involved fields are present in update_data
            # and at least one of them is changing, and none are being set to None (unless allowed by DB).
            fields_to_check = {f: update_data.get(f, getattr(db_obj, f)) for f in ['summary_type', 'summary_date']}
            is_changing = any(update_data.get(f) is not None and update_data.get(f) != getattr(db_obj, f) for f in ['summary_type', 'summary_date'])
            all_parts_not_none = all(fields_to_check[f] is not None for f in ['summary_type', 'summary_date'])

            if is_changing and all_parts_not_none:
                filters = [SysAnalyticsSummary.id != getattr(db_obj, 'id')]
                filters.append(SysAnalyticsSummary.summary_type == fields_to_check['summary_type'])
                filters.append(SysAnalyticsSummary.summary_date == fields_to_check['summary_date'])
                existing = db.query(SysAnalyticsSummary).filter(and_(*filters)).first()
                if existing:
                    values_str = ', '.join([f"{fields_to_check[c]}" for c in ['summary_type', 'summary_date']])
                    raise ValueError(_(f"Duplicate combination of values for fields: summary_type, summary_date. Values: [{values_str}]"))

            # Check composite uniqueness constraint 2 (fields: summary_type, summary_year, summary_month)
            # This check is complex: only validate if all involved fields are present in update_data
            # and at least one of them is changing, and none are being set to None (unless allowed by DB).
            fields_to_check = {f: update_data.get(f, getattr(db_obj, f)) for f in ['summary_type', 'summary_year', 'summary_month']}
            is_changing = any(update_data.get(f) is not None and update_data.get(f) != getattr(db_obj, f) for f in ['summary_type', 'summary_year', 'summary_month'])
            all_parts_not_none = all(fields_to_check[f] is not None for f in ['summary_type', 'summary_year', 'summary_month'])

            if is_changing and all_parts_not_none:
                filters = [SysAnalyticsSummary.id != getattr(db_obj, 'id')]
                filters.append(SysAnalyticsSummary.summary_type == fields_to_check['summary_type'])
                filters.append(SysAnalyticsSummary.summary_year == fields_to_check['summary_year'])
                filters.append(SysAnalyticsSummary.summary_month == fields_to_check['summary_month'])
                existing = db.query(SysAnalyticsSummary).filter(and_(*filters)).first()
                if existing:
                    values_str = ', '.join([f"{fields_to_check[c]}" for c in ['summary_type', 'summary_year', 'summary_month']])
                    raise ValueError(_(f"Duplicate combination of values for fields: summary_type, summary_year, summary_month. Values: [{values_str}]"))

            # Check composite uniqueness constraint 3 (fields: summary_type, region_name)
            # This check is complex: only validate if all involved fields are present in update_data
            # and at least one of them is changing, and none are being set to None (unless allowed by DB).
            fields_to_check = {f: update_data.get(f, getattr(db_obj, f)) for f in ['summary_type', 'region_name']}
            is_changing = any(update_data.get(f) is not None and update_data.get(f) != getattr(db_obj, f) for f in ['summary_type', 'region_name'])
            all_parts_not_none = all(fields_to_check[f] is not None for f in ['summary_type', 'region_name'])

            if is_changing and all_parts_not_none:
                filters = [SysAnalyticsSummary.id != getattr(db_obj, 'id')]
                filters.append(SysAnalyticsSummary.summary_type == fields_to_check['summary_type'])
                filters.append(SysAnalyticsSummary.region_name == fields_to_check['region_name'])
                existing = db.query(SysAnalyticsSummary).filter(and_(*filters)).first()
                if existing:
                    values_str = ', '.join([f"{fields_to_check[c]}" for c in ['summary_type', 'region_name']])
                    raise ValueError(_(f"Duplicate combination of values for fields: summary_type, region_name. Values: [{values_str}]"))

            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except Exception:
            db.rollback()
            logger.error(f"Failed to update SysAnalyticsSummary ({db_obj.id})", exc_info=True)
            raise

    def remove(self, db: Session, id: int) -> Optional[SysAnalyticsSummary]:
        """Delete SysAnalyticsSummary by ID"""
        try:
            obj = self.get(db, id) # Use self.get for consistency
            if obj:
                db.delete(obj)
                db.commit()
            return obj
        except Exception:
            db.rollback()
            logger.error(f"Failed to delete SysAnalyticsSummary (ID: {id})", exc_info=True)
            raise


# Helper class for chainable query building
class QueryBuilderSysAnalyticsSummary:
    def __init__(self, db: Session, query: Query, crud_base: CRUDSysAnalyticsSummary):
        self._db: Session = db
        self._query: Query = query
        self._crud_base: CRUDSysAnalyticsSummary = crud_base

    def filter(self, *criterion) -> 'QueryBuilderSysAnalyticsSummary':
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

    def get_all(self, db: Optional[Session] = None, search: Optional[str] = None, orderby: Optional[str] = None) -> List[SysAnalyticsSummary]:
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
    ) -> List[SysAnalyticsSummary]:
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

    def all(self) -> List[SysAnalyticsSummary]:
        """Directly execute .all() on the current query object."""
        return self._query.all()

    def first(self) -> Optional[SysAnalyticsSummary]:
        """Directly execute .first() on the current query object."""
        return self._query.first()

    def count(self) -> int:
        """Directly execute .count() on the current query object."""
        return self._query.count()


crud_sys_analytics_summary = CRUDSysAnalyticsSummary()
