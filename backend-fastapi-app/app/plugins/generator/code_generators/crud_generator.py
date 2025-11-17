from calendar import c
import logging
from typing import List, Optional, TypeVar
from sqlalchemy import TEXT, VARCHAR, String, Table
from sqlalchemy.engine.reflection import Inspector
from pydantic import BaseModel
from fastapi_babel import _

logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)



# Generate CRUD code
def generate_crud_code(
    inspector: any,
    table: Table,
    searchable_fields: Optional[List[str]] = None
) -> str:
    class_name = "".join(word.capitalize() for word in table.name.split("_"))
    primary_key_column = list(table.primary_key.columns)[0].name
    primary_key_type = "int" # 假设主键总是 int, 可以根据实际情况调整
    if hasattr(list(table.primary_key.columns)[0].type, 'python_type'):
        pk_python_type = list(table.primary_key.columns)[0].type.python_type
        if pk_python_type == str:
            primary_key_type = "str"
        elif pk_python_type == int:
            primary_key_type = "int"
        # 可以根据需要添加更多类型映射

    # Get unique constraints
    unique_constraints = inspector.get_unique_constraints(table.name)
    unique_columns = set()
    composite_unique_constraints = []

    # Process constraints
    for constraint in unique_constraints:
        if "column_names" in constraint:
            columns = constraint["column_names"]
            if len(columns) == 1:
                unique_columns.add(columns[0])
            else:
                composite_unique_constraints.append(columns)

    # Determine searchable fields
    if searchable_fields is None:
        search_columns = [col.name for col in table.columns if (isinstance(col.type, (String, TEXT, VARCHAR)) and col.name !='password')]
    else:
        search_columns = [col for col in searchable_fields if col in [c.name for c in table.columns]] # 确保提供的字段存在于表中

    # Generate imports
    imports = (
        f"from typing import List, Optional, Dict, Any, Union, TYPE_CHECKING\n"
        f"from fastapi_babel import _\n"
        f"from sqlalchemy.orm import Session, Query\n"
        f"from sqlalchemy import and_, or_\n"
        f"from app.models.{table.name} import {class_name}\n"
        f"from app.schemas.{table.name} import {class_name}Create, {class_name}Update\n"
        f"from app.utils.log_utils import logger\n\n"
        f"# Forward declaration for QueryBuilder to avoid circular import issues\n"
        f"if TYPE_CHECKING:\n"
        f"    class _QueryBuilder{class_name}:\n"
        f"        pass\n\n"
    )

    # Start CRUD class
    crud_class = f"class CRUD{class_name}:\n"

    # Add SEARCHABLE_FIELDS class variable
    if search_columns:
        crud_class += f"    SEARCHABLE_FIELDS = {search_columns}\n\n"
    else:
        crud_class += f"    SEARCHABLE_FIELDS: List[str] = [] # No searchable fields defined\n\n"


    # get method
    crud_class += f"    def get(self, db: Session, {primary_key_column}: {primary_key_type}) -> Optional[{class_name}]:\n" # 使用 primary_key_type
    crud_class += f'        """Get {class_name} by ID"""\n'
    crud_class += f"        return db.get({class_name},{primary_key_column})\n\n"

    # Private methods
    crud_class += f"    def _apply_search_filter(self, query: Query, search: Optional[str]) -> Query:\n" # Type hint Query
    crud_class += f'        """Apply search filter"""\n'
    crud_class += f"        if not search or not self.SEARCHABLE_FIELDS:\n" # 简化条件
    crud_class += f"            return query\n"
    crud_class += f"        \n"
    crud_class += f'        search_pattern = f"%{{search}}%"\n'
    crud_class += f"        filters = []\n"
    crud_class += f"        for field in self.SEARCHABLE_FIELDS:\n"
    crud_class += f"            if hasattr({class_name}, field):\n" # Check if field exists on model
    crud_class += f"                filters.append(getattr({class_name}, field).ilike(search_pattern))\n"
    crud_class += f"        if not filters:\n" # If no valid searchable fields found
    crud_class += f"             return query\n"
    crud_class += f"        return query.filter(or_(*filters))\n\n"

    crud_class += f"    def _apply_order_by(self, query: Query, orderby: Optional[str]) -> Query:\n" # Type hint Query
    crud_class += f'        """Apply ordering"""\n'
    crud_class += f"        if not orderby:\n"
    crud_class += f"            return query\n"
    crud_class += f"        \n"
    crud_class += f"        try:\n"
    crud_class += f'            field, direction = orderby.rsplit("_", 1)\n'
    crud_class += f"            if not hasattr({class_name}, field):\n" # Check if field exists
    crud_class += f'                logger.error(_(f"Invalid sort field: {{field}} for model {class_name}"))\n'
    crud_class += f"                return query\n"
    crud_class += f"            order_column = getattr({class_name}, field)\n"
    crud_class += f'            if direction.lower() == "asc":\n' # Use lower() for case-insensitivity
    crud_class += f"                return query.order_by(order_column.asc())\n"
    crud_class += f'            elif direction.lower() == "desc":\n'
    crud_class += f"                return query.order_by(order_column.desc())\n"
    crud_class += f'            logger.warning(_(f"Invalid sort direction: {{direction}} for field {{field}}"))\n' # Log invalid direction
    crud_class += f"            return query\n"
    crud_class += f"        except ValueError: # Handles rsplit error if '_' not found\n"
    crud_class += f'            logger.error(_("Invalid orderby format. Expected format: field_direction"))\n'
    crud_class += f"            return query\n"
    crud_class += f"        except AttributeError: # Should be caught by hasattr check, but as a fallbacky\n"
    crud_class += f'            logger.error(_(f"Sort field does not exist on model {class_name}"))\n'
    crud_class += f"            return query\n\n"

    # filter method
    crud_class += f"    def filter(self, db: Session, *criterion) -> 'QueryBuilder{class_name}':\n"
    crud_class += f'        """\n'
    crud_class += f'        Apply custom SQLAlchemy filter criteria and return a QueryBuilder instance.\n'
    crud_class += f'        Allows for chainable calls like .get_all(), .get_multi(), etc.\n'
    crud_class += f'        Args:\n'
    crud_class += f'            db (Session): SQLAlchemy database session.\n'
    crud_class += f'            *criterion: One or more SQLAlchemy filter expressions\n'
    crud_class += f'                        (e.g., {class_name}.name == "example", {class_name}.status == 1).\n'
    crud_class += f'        """\n'
    crud_class += f"        initial_query = db.query({class_name})\n"
    crud_class += f"        if criterion:\n"
    crud_class += f"            initial_query = initial_query.filter(*criterion)\n"
    crud_class += f"        return QueryBuilder{class_name}(db=db, query=initial_query, crud_base=self)\n\n"

    # get_multi method
    crud_class += f"    def get_multi(\n"
    crud_class += f"        self, \n"
    crud_class += f"        db: Session, \n"
    crud_class += f"        page: int = 1, \n"
    crud_class += f"        per_page: int = 10, \n"
    crud_class += f"        search: Optional[str] = None, \n"
    crud_class += f"        orderby: Optional[str] = None,\n"
    crud_class += f"        base_query: Optional[Query] = None\n" # Added base_query
    crud_class += f"    ) -> List[{class_name}]:\n"
    crud_class += f'        """Get paginated list of {class_name} records"""\n'
    crud_class += f"        page = max(1, page)\n"
    crud_class += f"        per_page = max(1, min(per_page, 100))\n"
    crud_class += f"        \n"
    crud_class += f"        query = base_query if base_query is not None else db.query({class_name})\n" # Use base_query if provided
    crud_class += f"        query = self._apply_search_filter(query, search)\n"
    crud_class += f"        query = self._apply_order_by(query, orderby)\n"
    crud_class += f"        \n"
    crud_class += f"        return query.offset((page - 1) * per_page).limit(per_page).all()\n\n"

    # get_all method
    crud_class += f"    def get_all(\n"
    crud_class += f"        self, \n"
    crud_class += f"        db: Session, \n"
    crud_class += f"        search: Optional[str] = None, \n"
    crud_class += f"        orderby: Optional[str] = None,\n"
    crud_class += f"        base_query: Optional[Query] = None\n" # Added base_query
    crud_class += f"    ) -> List[{class_name}]:\n"
    crud_class += f'        """Get all {class_name} records"""\n'
    crud_class += f"        query = base_query if base_query is not None else db.query({class_name})\n" # Use base_query if provided
    crud_class += f"        query = self._apply_search_filter(query, search)\n"
    crud_class += f"        query = self._apply_order_by(query, orderby)\n"
    crud_class += f"        return query.all()\n\n"

    # get_total method
    crud_class += f"    def get_total(self, db: Session, search: Optional[str] = None, base_query: Optional[Query] = None) -> int:\n" # Added base_query
    crud_class += f'        """Get total count of {class_name} records"""\n'
    crud_class += f"        query = base_query if base_query is not None else db.query({class_name})\n" # Use base_query if provided
    crud_class += f"        query = self._apply_search_filter(query, search)\n"
    crud_class += f"        # Order by is not needed for count\n"
    crud_class += f"        return query.count()\n\n"

    # create method
    crud_class += f"    def create(self, db: Session, obj_in: {class_name}Create) -> {class_name}:\n"
    crud_class += f'        """Create new {class_name} record with uniqueness validation"""\n'
    crud_class += f"        try:\n"
    for col in unique_columns:
        crud_class += f"            # Check {col} uniqueness\n"
        crud_class += f"            if hasattr(obj_in, '{col}') and getattr(obj_in, '{col}') is not None:\n" # Check if None
        crud_class += f"                existing = db.query({class_name}).filter(\n"
        crud_class += f"                    {class_name}.{col} == getattr(obj_in, '{col}')\n"
        crud_class += f"                ).first()\n"
        crud_class += f"                if existing:\n"
        crud_class += f"                    raise ValueError(_(f\"Duplicate value for {col}: '{{getattr(obj_in, '{col}')}}'\"))\n\n"
    for i, columns in enumerate(composite_unique_constraints, 1):
        columns_str = ', '.join(columns)
        crud_class += f"            # Check composite uniqueness constraint {i} (fields: {columns_str})\n"
        crud_class += f"            filters = []\n"
        crud_class += f"            all_fields_present = True\n"
        for col_idx, col in enumerate(columns):
            crud_class += f"            if hasattr(obj_in, '{col}') and getattr(obj_in, '{col}') is not None:\n"
            crud_class += f"                filters.append({class_name}.{col} == getattr(obj_in, '{col}'))\n"
            crud_class += f"            else:\n"
            crud_class += f"                all_fields_present = False # If any part of composite key is None, skip check or handle as per policy\n"
            crud_class += f"                # Depending on DB, NULLs might not be considered equal for unique constraints.\n"
            crud_class += f"                # For now, if any part is None, we assume it won't cause a unique violation by itself.\n"
            crud_class += f"                # If your DB treats NULLs as equal in unique constraints, this logic needs adjustment.\n"
            crud_class += f"                # Skip this constraint check if any field is None\n"
            crud_class += f"                continue_check = False\n"
        crud_class += f"            if all_fields_present and len(filters) == {len(columns)}:\n"
        crud_class += f"                existing = db.query({class_name}).filter(and_(*filters)).first()\n"
        crud_class += f"                if existing:\n"
        crud_class += f"                    values_str = ', '.join([f\"{{getattr(obj_in, '{c}')}}\" for c in {columns}])\n"
        crud_class += f"                    raise ValueError(_(f\"Duplicate combination of values for fields: {columns_str}. Values: []\"))\n\n"
    crud_class += f"            db_obj = {class_name}(**obj_in.model_dump(exclude_unset=True))\n"
    crud_class += f"            db.add(db_obj)\n"
    crud_class += f"            db.commit()\n"
    crud_class += f"            db.refresh(db_obj)\n"
    crud_class += f"            return db_obj\n"
    crud_class += f"        except Exception:\n"
    crud_class += f"            db.rollback()\n"
    crud_class += f"            logger.error(f\"Failed to create {class_name}\", exc_info=True)\n"
    crud_class += f"            raise\n\n"

    # update method
    crud_class += f"    def update(\n"
    crud_class += f"        self, \n"
    crud_class += f"        db: Session, \n"
    crud_class += f"        db_obj: {class_name}, \n"
    crud_class += f"        obj_in: Union[Dict[str, Any], {class_name}Update]\n"
    crud_class += f"    ) -> {class_name}:\n"
    crud_class += f'        """Update existing {class_name} record with uniqueness validation"""\n'
    crud_class += f"        try:\n"
    crud_class += f"            update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)\n"
    for col in unique_columns:
        crud_class += f"            # Check {col} uniqueness if being changed\n"
        crud_class += f"            if '{col}' in update_data and update_data['{col}'] is not None:\n" # Check if None
        crud_class += f"                new_{col} = update_data['{col}']\n"
        crud_class += f"                if new_{col} != getattr(db_obj, '{col}'):\n"
        crud_class += f"                    existing = db.query({class_name}).filter(\n"
        crud_class += f"                        {class_name}.{col} == new_{col},\n"
        crud_class += f"                        {class_name}.{primary_key_column} != getattr(db_obj, '{primary_key_column}')\n"
        crud_class += f"                    ).first()\n"
        crud_class += f"                    if existing:\n"
        crud_class += f"                        raise ValueError(_(f\"Duplicate value for {col}: '{{new_{col}}}'\"))\n\n"
    for i, columns in enumerate(composite_unique_constraints, 1):
        columns_str = ', '.join(columns)
        crud_class += f"            # Check composite uniqueness constraint {i} (fields: {columns_str})\n"
        crud_class += f"            # This check is complex: only validate if all involved fields are present in update_data\n"
        crud_class += f"            # and at least one of them is changing, and none are being set to None (unless allowed by DB).\n"
        crud_class += f"            fields_to_check = {{f: update_data.get(f, getattr(db_obj, f)) for f in {columns}}}\n"
        crud_class += f"            is_changing = any(update_data.get(f) is not None and update_data.get(f) != getattr(db_obj, f) for f in {columns})\n"
        crud_class += f"            all_parts_not_none = all(fields_to_check[f] is not None for f in {columns})\n\n"
        crud_class += f"            if is_changing and all_parts_not_none:\n"
        crud_class += f"                filters = [{class_name}.{primary_key_column} != getattr(db_obj, '{primary_key_column}')]\n"
        for col in columns:
            crud_class += f"                filters.append({class_name}.{col} == fields_to_check['{col}'])\n"
        crud_class += f"                existing = db.query({class_name}).filter(and_(*filters)).first()\n"
        crud_class += f"                if existing:\n"
        crud_class += f"                    values_str = ', '.join([f\"{{fields_to_check['{c}']}}\" for c in {columns}])\n"
        crud_class += f"                    raise ValueError(_(f\"Duplicate combination of values for fields: {columns_str}. Values: []\"))\n\n"

    crud_class += f"            for field, value in update_data.items():\n"
    crud_class += f"                if hasattr(db_obj, field):\n" # Ensure field exists before setting
    crud_class += f"                    setattr(db_obj, field, value)\n"
    crud_class += f"            \n"
    crud_class += f"            db.commit()\n"
    crud_class += f"            db.refresh(db_obj)\n"
    crud_class += f"            return db_obj\n"
    crud_class += f"        except Exception:\n"
    crud_class += f"            db.rollback()\n"
    # Assuming the model always has an 'id' field for logging, or use primary_key_column
    id_attr_for_log = "id" if "id" in [c.name for c in table.columns] else primary_key_column
    crud_class += f"            logger.error(f\"Failed to update {class_name} ({{db_obj.{id_attr_for_log}}})\", exc_info=True)\n"
    crud_class += f"            raise\n\n"

    # remove method
    crud_class += f"    def remove(self, db: Session, {primary_key_column}: {primary_key_type}) -> Optional[{class_name}]:\n" # 使用 primary_key_type
    crud_class += f'        """Delete {class_name} by ID"""\n'
    crud_class += f"        try:\n"
    crud_class += f"            obj = self.get(db, {primary_key_column}) # Use self.get for consistency\n"
    crud_class += f"            if obj:\n"
    crud_class += f"                db.delete(obj)\n"
    crud_class += f"                db.commit()\n"
    crud_class += f"            return obj\n"
    crud_class += f"        except Exception:\n"
    crud_class += f"            db.rollback()\n"
    crud_class += f"            logger.error(f\"Failed to delete {class_name} (ID: {{{primary_key_column}}})\", exc_info=True)\n"
    crud_class += f"            raise\n\n"

    # Add QueryBuilder class
    query_builder_class = f"\n# Helper class for chainable query building\n"
    query_builder_class += f"class QueryBuilder{class_name}:\n"
    query_builder_class += f"    def __init__(self, db: Session, query: Query, crud_base: CRUD{class_name}):\n"
    query_builder_class += f"        self._db: Session = db\n"
    query_builder_class += f"        self._query: Query = query\n"
    query_builder_class += f"        self._crud_base: CRUD{class_name} = crud_base\n\n"

    query_builder_class += f"    def filter(self, *criterion) -> 'QueryBuilder{class_name}':\n"
    query_builder_class += f'        """Apply additional filter criteria to the current query."""\n'
    query_builder_class += f"        if criterion:\n"
    query_builder_class += f"            self._query = self._query.filter(*criterion)\n"
    query_builder_class += f"        return self\n\n"

    query_builder_class += f"    def _get_effective_db(self, db_param: Optional[Session]) -> Session:\n"
    query_builder_class += f'        """Determine the actual database session to use. Prefers the initial session."""\n'
    query_builder_class += f"        if db_param is not None and db_param is not self._db:\n"
    query_builder_class += f'            logger.warning(\n'
    query_builder_class += f'                "QueryBuilder method called with a DB session different from its initial one. "\n'
    query_builder_class += f'                "The initial session will be used for the query execution."\n'
    query_builder_class += f'            )\n'
    query_builder_class += f"        return self._db\n\n"

    query_builder_class += f"    def get_all(self, db: Optional[Session] = None, search: Optional[str] = None, orderby: Optional[str] = None) -> List[{class_name}]:\n"
    query_builder_class += f'        """Execute the query and return all results, applying optional search and ordering."""\n'
    query_builder_class += f"        effective_db = self._get_effective_db(db)\n"
    query_builder_class += f"        return self._crud_base.get_all(db=effective_db, search=search, orderby=orderby, base_query=self._query)\n\n"

    query_builder_class += f"    def get_multi(\n"
    query_builder_class += f"        self, \n"
    query_builder_class += f"        db: Optional[Session] = None,\n"
    query_builder_class += f"        page: int = 1, \n"
    query_builder_class += f"        per_page: int = 10, \n"
    query_builder_class += f"        search: Optional[str] = None, \n"
    query_builder_class += f"        orderby: Optional[str] = None\n"
    query_builder_class += f"    ) -> List[{class_name}]:\n"
    query_builder_class += f'        """Execute the query with pagination, applying optional search and ordering."""\n'
    query_builder_class += f"        effective_db = self._get_effective_db(db)\n"
    query_builder_class += f"        return self._crud_base.get_multi(\n"
    query_builder_class += f"            db=effective_db, \n"
    query_builder_class += f"            page=page, \n"
    query_builder_class += f"            per_page=per_page, \n"
    query_builder_class += f"            search=search, \n"
    query_builder_class += f"            orderby=orderby, \n"
    query_builder_class += f"            base_query=self._query\n"
    query_builder_class += f"        )\n\n"

    query_builder_class += f"    def get_total(self, db: Optional[Session] = None, search: Optional[str] = None) -> int:\n"
    query_builder_class += f'        """Execute the query to get the total count of records, applying optional search."""\n'
    query_builder_class += f"        effective_db = self._get_effective_db(db)\n"
    query_builder_class += f"        return self._crud_base.get_total(db=effective_db, search=search, base_query=self._query)\n\n"

    query_builder_class += f"    def all(self) -> List[{class_name}]:\n"
    query_builder_class += f'        """Directly execute .all() on the current query object."""\n'
    query_builder_class += f"        return self._query.all()\n\n"

    query_builder_class += f"    def first(self) -> Optional[{class_name}]:\n"
    query_builder_class += f'        """Directly execute .first() on the current query object."""\n'
    query_builder_class += f"        return self._query.first()\n\n"
    
    query_builder_class += f"    def count(self) -> int:\n"
    query_builder_class += f'        """Directly execute .count() on the current query object."""\n'
    query_builder_class += f"        return self._query.count()\n"


    # Instantiate CRUD class
    instantiation = f"\n\ncrud_{table.name} = CRUD{class_name}()\n"

    # Combine all parts
    full_code = imports + crud_class + query_builder_class + instantiation
    return full_code
