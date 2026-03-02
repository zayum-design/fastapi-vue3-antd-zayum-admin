from typing import Any

from fastapi_babel import _
from sqlalchemy import or_
from sqlalchemy.orm import Query, Session

from app.modules.admin.sys_admin.models.sys_admin import SysAdmin
from app.modules.admin.sys_admin.schemas.sys_admin import SysAdminCreate, SysAdminUpdate
from app.utils.log_utils import logger


class CRUDSysAdmin:
    SEARCHABLE_FIELDS = [
        "username",
        "nickname",
        "avatar",
        "email",
        "mobile",
        "login_ip",
        "token",
        "status",
    ]

    def get(self, db: Session, id: int) -> SysAdmin | None:
        """Get SysAdmin by ID"""
        return db.get(SysAdmin, id)

    def _apply_search_filter(self, query: Query, search: str | None) -> Query:
        """Apply search filter"""
        if not search or not self.SEARCHABLE_FIELDS:
            return query

        search_pattern = f"%{search}%"
        filters = []
        for field in self.SEARCHABLE_FIELDS:
            if hasattr(SysAdmin, field):
                filters.append(getattr(SysAdmin, field).ilike(search_pattern))
        if not filters:
            return query
        return query.filter(or_(*filters))

    def _apply_order_by(self, query: Query, orderby: str | None) -> Query:
        """Apply ordering"""
        if not orderby:
            return query

        try:
            field, direction = orderby.rsplit("_", 1)
            if not hasattr(SysAdmin, field):
                logger.error(_("Invalid sort field: {field} for model SysAdmin"))
                return query
            order_column = getattr(SysAdmin, field)
            if direction.lower() == "asc":
                return query.order_by(order_column.asc())
            elif direction.lower() == "desc":
                return query.order_by(order_column.desc())
            logger.warning(_("Invalid sort direction: {direction} for field {field}"))
            return query
        except ValueError:  # Handles rsplit error if '_' not found
            logger.error(_("Invalid orderby format. Expected format: field_direction"))
            return query
        except AttributeError:  # Should be caught by hasattr check, but as a fallbacky
            logger.error(_("Sort field does not exist on model SysAdmin"))
            return query

    def filter(self, db: Session, *criterion) -> "QueryBuilderSysAdmin":
        """
        Apply custom SQLAlchemy filter criteria and return a QueryBuilder instance.
        Allows for chainable calls like .get_all(), .get_multi(), etc.
        Args:
            db (Session): SQLAlchemy database session.
            *criterion: One or more SQLAlchemy filter expressions
                        (e.g., SysAdmin.name == "example", SysAdmin.status == 1).
        """
        initial_query = db.query(SysAdmin)
        if criterion:
            initial_query = initial_query.filter(*criterion)
        return QueryBuilderSysAdmin(db=db, query=initial_query, crud_base=self)

    def get_multi(
        self,
        db: Session,
        page: int = 1,
        per_page: int = 10,
        search: str | None = None,
        orderby: str | None = None,
        base_query: Query | None = None,
    ) -> list[SysAdmin]:
        """Get paginated list of SysAdmin records"""
        page = max(1, page)
        per_page = max(1, min(per_page, 100))

        query = base_query if base_query is not None else db.query(SysAdmin)
        query = self._apply_search_filter(query, search)
        query = self._apply_order_by(query, orderby)

        return query.offset((page - 1) * per_page).limit(per_page).all()

    def get_all(
        self,
        db: Session,
        search: str | None = None,
        orderby: str | None = None,
        base_query: Query | None = None,
    ) -> list[SysAdmin]:
        """Get all SysAdmin records"""
        query = base_query if base_query is not None else db.query(SysAdmin)
        query = self._apply_search_filter(query, search)
        query = self._apply_order_by(query, orderby)
        return query.all()

    def get_total(
        self, db: Session, search: str | None = None, base_query: Query | None = None
    ) -> int:
        """Get total count of SysAdmin records"""
        query = base_query if base_query is not None else db.query(SysAdmin)
        query = self._apply_search_filter(query, search)
        # Order by is not needed for count
        return query.count()

    def create(self, db: Session, obj_in: SysAdminCreate) -> SysAdmin:
        """Create new SysAdmin record with uniqueness validation"""
        try:
            # Check username uniqueness
            if hasattr(obj_in, "username") and obj_in.username is not None:
                existing = db.query(SysAdmin).filter(SysAdmin.username == obj_in.username).first()
                if existing:
                    raise ValueError(
                        _("Duplicate value for username: '{getattr(obj_in, 'username')}'")
                    )

            # Check mobile uniqueness
            if hasattr(obj_in, "mobile") and obj_in.mobile is not None:
                existing = db.query(SysAdmin).filter(SysAdmin.mobile == obj_in.mobile).first()
                if existing:
                    raise ValueError(_("Duplicate value for mobile: '{getattr(obj_in, 'mobile')}'"))

            # Check email uniqueness
            if hasattr(obj_in, "email") and obj_in.email is not None:
                existing = db.query(SysAdmin).filter(SysAdmin.email == obj_in.email).first()
                if existing:
                    raise ValueError(_("Duplicate value for email: '{getattr(obj_in, 'email')}'"))

            db_obj = SysAdmin(**obj_in.model_dump(exclude_unset=True))
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except Exception:
            db.rollback()
            logger.error("Failed to create SysAdmin", exc_info=True)
            raise

    def update(
        self, db: Session, db_obj: SysAdmin, obj_in: dict[str, Any] | SysAdminUpdate
    ) -> SysAdmin:
        """Update existing SysAdmin record with uniqueness validation"""
        try:
            update_data = (
                obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
            )
            # Check username uniqueness if being changed
            if "username" in update_data and update_data["username"] is not None:
                new_username = update_data["username"]
                if new_username != db_obj.username:
                    existing = (
                        db.query(SysAdmin)
                        .filter(SysAdmin.username == new_username, SysAdmin.id != db_obj.id)
                        .first()
                    )
                    if existing:
                        raise ValueError(_("Duplicate value for username: '{new_username}'"))

            # Check mobile uniqueness if being changed
            if "mobile" in update_data and update_data["mobile"] is not None:
                new_mobile = update_data["mobile"]
                if new_mobile != db_obj.mobile:
                    existing = (
                        db.query(SysAdmin)
                        .filter(SysAdmin.mobile == new_mobile, SysAdmin.id != db_obj.id)
                        .first()
                    )
                    if existing:
                        raise ValueError(_("Duplicate value for mobile: '{new_mobile}'"))

            # Check email uniqueness if being changed
            if "email" in update_data and update_data["email"] is not None:
                new_email = update_data["email"]
                if new_email != db_obj.email:
                    existing = (
                        db.query(SysAdmin)
                        .filter(SysAdmin.email == new_email, SysAdmin.id != db_obj.id)
                        .first()
                    )
                    if existing:
                        raise ValueError(_("Duplicate value for email: '{new_email}'"))

            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)

            db.commit()
            db.refresh(db_obj)
            return db_obj
        except Exception:
            db.rollback()
            logger.error("Failed to update SysAdmin ({db_obj.id})", exc_info=True)
            raise

    def remove(self, db: Session, id: int) -> SysAdmin | None:
        """Delete SysAdmin by ID"""
        try:
            obj = self.get(db, id)  # Use self.get for consistency
            if obj:
                db.delete(obj)
                db.commit()
            return obj
        except Exception:
            db.rollback()
            logger.error("Failed to delete SysAdmin (ID: {id})", exc_info=True)
            raise


# Helper class for chainable query building
class QueryBuilderSysAdmin:
    def __init__(self, db: Session, query: Query, crud_base: CRUDSysAdmin):
        self._db: Session = db
        self._query: Query = query
        self._crud_base: CRUDSysAdmin = crud_base

    def filter(self, *criterion) -> "QueryBuilderSysAdmin":
        """Apply additional filter criteria to the current query."""
        if criterion:
            self._query = self._query.filter(*criterion)
        return self

    def _get_effective_db(self, db_param: Session | None) -> Session:
        """Determine the actual database session to use. Prefers the initial session."""
        if db_param is not None and db_param is not self._db:
            logger.warning(
                "QueryBuilder method called with a DB session different from its initial one. "
                "The initial session will be used for the query execution."
            )
        return self._db

    def get_all(
        self, db: Session | None = None, search: str | None = None, orderby: str | None = None
    ) -> list[SysAdmin]:
        """Execute the query and return all results, applying optional search and ordering."""
        effective_db = self._get_effective_db(db)
        return self._crud_base.get_all(
            db=effective_db, search=search, orderby=orderby, base_query=self._query
        )

    def get_multi(
        self,
        db: Session | None = None,
        page: int = 1,
        per_page: int = 10,
        search: str | None = None,
        orderby: str | None = None,
    ) -> list[SysAdmin]:
        """Execute the query with pagination, applying optional search and ordering."""
        effective_db = self._get_effective_db(db)
        return self._crud_base.get_multi(
            db=effective_db,
            page=page,
            per_page=per_page,
            search=search,
            orderby=orderby,
            base_query=self._query,
        )

    def get_total(self, db: Session | None = None, search: str | None = None) -> int:
        """Execute the query to get the total count of records, applying optional search."""
        effective_db = self._get_effective_db(db)
        return self._crud_base.get_total(db=effective_db, search=search, base_query=self._query)

    def all(self) -> list[SysAdmin]:
        """Directly execute .all() on the current query object."""
        return self._query.all()

    def first(self) -> SysAdmin | None:
        """Directly execute .first() on the current query object."""
        return self._query.first()

    def count(self) -> int:
        """Directly execute .count() on the current query object."""
        return self._query.count()


crud_sys_admin = CRUDSysAdmin()
