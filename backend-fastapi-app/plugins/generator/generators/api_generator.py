"""
API代码生成器
生成FastAPI路由代码
"""

from sqlalchemy import Table


class ApiGenerator:
    """API代码生成器类"""
    
    def generate(self, table: Table) -> str:
        """生成API代码"""
        class_name = "".join(word.capitalize() for word in table.name.split("_"))
        table_name = table.name
        
        # 获取主键列
        primary_key_columns = [col.name for col in table.primary_key.columns]
        primary_key = primary_key_columns[0] if primary_key_columns else "id"
        
        # 构建API代码
        api_code = f'''from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi_babel import _
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.core.security import get_current_admin
from app.modules.admin.{table_name}.crud.{table_name} import crud_{table_name}
from app.modules.admin.{table_name}.schemas.{table_name} import {class_name}Create, {class_name}Update
from app.utils.responses import success_response
from app.utils.response_handlers import ErrorCode
from app.modules.admin.{table_name}.models.{table_name} import {class_name}

# Initialize the API router for {table.name} endpoints
router = APIRouter(
    prefix="/{table.name.removeprefix('sys_').replace('_', '/')}", tags=["{table.name.removeprefix('sys_')}"], dependencies=[Depends(get_current_admin)]
)

# Set the maximum per_page limit
MAX_PER_PAGE = 200


@router.get("/list")
def read_{table.name}_list(
    page: int = 1,
    per_page: int = 10,
    search: Optional[str] = None,
    orderby: Optional[str] = None,  # Sorting field and direction, e.g., "name_asc"
    db: Session = Depends(get_db)
):
    \"\"\"
    Retrieve a list of {class_name} records with optional pagination, search, and sorting.

    Args:
        page (int, optional): The page number to retrieve. Defaults to 1.
        per_page (int, optional): Number of records per page. Use -1 to retrieve all records. Defaults to 10.
        search (str, optional): A search string to filter records by relevant fields.
        orderby (str, optional): Sorting rule, e.g., "field_asc" or "field_desc".
        db (Session): Database session dependency.

    Returns:
        JSON response containing the list of records, total count, current page, and records per page.
    \"\"\"
    # If per_page is -1, set it to the maximum allowed value
    if per_page == -1:
        per_page = MAX_PER_PAGE  # Set per_page to the maximum value (200)
    
    # Ensure per_page is within the allowed range
    per_page = min(per_page, MAX_PER_PAGE)
    
    # Ensure page and per_page are at least 1
    page = max(page, 1)
    
    # Retrieve paginated records with search and sorting
    items = crud_{table.name}.get_multi(db, page=page, per_page=per_page, search=search, orderby=orderby)
    total = crud_{table.name}.get_total(db, search=search)
    
    response_page = page
    response_per_page = per_page

    # Prepare the response data
    return success_response(
        {{
            "items": [item.to_dict() for item in items],  # Convert each model instance to a dictionary
            "total": total,
            "page": response_page,
            "per_page": response_per_page,
        }}
    )


@router.get("/{{{primary_key}}}")
def read_{table.name}({primary_key}: int, db: Session = Depends(get_db)):
    \"\"\"
    Retrieve a single {class_name} record by its unique ID.

    Args:
        {primary_key} (int): The unique identifier of the {class_name}.
        db (Session): Database session dependency.

    Raises:
        HTTPException: If the record with the specified ID is not found.

    Returns:
        JSON response containing the record's data.
    \"\"\"
    db_obj = crud_{table.name}.get(db, {primary_key}={primary_key})
    if db_obj is None:
        # Raise a 404 Not Found error if the record does not exist
        raise HTTPException(status_code=ErrorCode.NOT_FOUND.value, detail=_("{class_name} not found."))
    # Return the record's data as a dictionary
    return success_response(db_obj.to_dict())


@router.post("/create")
def create_{table.name}(obj_in: {class_name}Create, db: Session = Depends(get_db)):
    \"\"\"
    Create a new {class_name} record.

    Args:
        obj_in ({class_name}Create): The schema containing the record's creation data.
        db (Session): Database session dependency.

    Returns:
        JSON response containing the ID of the newly created record.
    \"\"\"
    ret = crud_{table.name}.create(db, obj_in=obj_in)
    # Return the ID of the inserted record
    return success_response({{"insert_id": ret.{primary_key}}})


@router.put("/update/{{{primary_key}}}")
def update_{table.name}({primary_key}: int, obj_in: {class_name}Update, db: Session = Depends(get_db)):
    \"\"\"
    Update an existing {class_name} record.

    Args:
        {primary_key} (int): The unique identifier of the {class_name} to update.
        obj_in ({class_name}Update): The schema containing the updated data.
        db (Session): Database session dependency.

    Raises:
        HTTPException: If the record with the specified ID is not found.

    Returns:
        JSON response containing the updated record's data.
    \"\"\"
    db_obj = crud_{table.name}.get(db, {primary_key}={primary_key})
    if not db_obj:
        # Raise a 404 Not Found error if the record does not exist
        raise HTTPException(status_code=ErrorCode.NOT_FOUND.value, detail=_("{class_name} not found."))
    # Update the record with the provided data
    updated_obj = crud_{table.name}.update(
        db, db_obj=db_obj, obj_in=obj_in.model_dump(exclude_unset=True)
    )
    # Return the updated record's data as a dictionary
    return success_response(updated_obj.to_dict())


@router.delete("/delete/{{{primary_key}}}")
def delete_{table.name}({primary_key}: int, db: Session = Depends(get_db)):
    \"\"\"
    Delete a {class_name} record by its unique ID.

    Args:
        {primary_key} (int): The unique identifier of the {class_name} to delete.
        db (Session): Database session dependency.

    Raises:
        HTTPException: If the record with the specified ID is not found.

    Returns:
        JSON response indicating successful deletion.
    \"\"\"
    db_obj = crud_{table.name}.get(db, {primary_key}={primary_key})
    if db_obj is None:
        # Raise a 404 Not Found error if the record does not exist
        raise HTTPException(status_code=ErrorCode.NOT_FOUND.value, detail=_("{class_name} not found."))
    # Remove the record from the database
    crud_{table.name}.remove(db, {primary_key}={primary_key})
    # Return an empty success response
    return success_response({{}})
'''
        return api_code
