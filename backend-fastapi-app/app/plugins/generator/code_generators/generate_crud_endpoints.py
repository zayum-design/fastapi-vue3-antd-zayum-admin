 
from sqlalchemy.types import TypeEngine
from sqlalchemy import Enum as SqlEnum
from typing import Dict, List, Union
import datetime
import decimal
import enum
import re
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import (
    BOOLEAN,
    DATE,
    DATETIME,
    DECIMAL,
    INTEGER,
    SMALLINT,
    TEXT,
    VARCHAR,
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    inspect,
    MetaData,
    Table,
    Enum as SqlEnum,
    JSON,
)
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import logging
from pathlib import Path
from app.utils.responses import success_response
from app.dependencies.database import get_db
from app.core.security import get_current_admin
from app.utils.log_utils import logger


def generate_crud_endpoints(table: Table) -> str:
    """
    Generate FastAPI CRUD endpoints for a given SQLAlchemy table,
    adhering to specific routing and response patterns.

    Args:
        table (Table): The SQLAlchemy table object for which to generate endpoints.

    Returns:
        str: A string containing the generated FastAPI CRUD endpoint code.
    """
    # Derive class name by capitalizing each part of the table name
    class_name = "".join(word.capitalize() for word in table.name.split("_"))

    # Assume the first primary key column is the identifier
    primary_key_column = list(table.primary_key.columns)[0].name

    # Start constructing the API code as a string
    api_code = f"""from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi_babel import _
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.core.security import get_current_admin
from app.crud.{table.name} import crud_{table.name}
from app.schemas.{table.name} import {class_name}Create, {class_name}Update
from app.utils.responses import success_response
from app.utils.response_handlers import ErrorCode
from app.models.{table.name} import {class_name} as {class_name}Model

# Initialize the API router for {table.name} endpoints
router = APIRouter(
    prefix="/{table.name.removeprefix('sys_').replace('_', '/')}", tags=["{table.name.removeprefix('sys_')}"], dependencies=[Depends(get_current_admin)]
)

# Set the maximum per_page limit
MAX_PER_PAGE = 200
"""

    # Generate the list endpoint with pagination, search, and sorting
    api_code += f"""@router.get("/list")
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
"""

    # Generate the single item retrieval endpoint
    api_code += f"""@router.get("/{{{primary_key_column}}}")
def read_{table.name}({primary_key_column}: int, db: Session = Depends(get_db)):
    \"\"\"
    Retrieve a single {class_name} record by its unique ID.

    Args:
        {primary_key_column} (int): The unique identifier of the {class_name}.
        db (Session): Database session dependency.

    Raises:
        HTTPException: If the record with the specified ID is not found.

    Returns:
        JSON response containing the record's data.
    \"\"\"
    db_obj = crud_{table.name}.get(db, {primary_key_column}={primary_key_column})
    if db_obj is None:
        # Raise a 404 Not Found error if the record does not exist
        raise HTTPException(status_code=ErrorCode.NOT_FOUND.value, detail=_("{class_name} not found."))
    # Return the record's data as a dictionary
    return success_response(db_obj.to_dict())
"""

    # Generate the create endpoint
    api_code += f"""@router.post("/create")
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
    return success_response({{"insert_id": ret.{primary_key_column}}})
"""

    # Generate the update endpoint
    api_code += f"""@router.put("/update/{{{primary_key_column}}}")
def update_{table.name}({primary_key_column}: int, obj_in: {class_name}Update, db: Session = Depends(get_db)):
    \"\"\"
    Update an existing {class_name} record.

    Args:
        {primary_key_column} (int): The unique identifier of the {class_name} to update.
        obj_in ({class_name}Update): The schema containing the updated data.
        db (Session): Database session dependency.

    Raises:
        HTTPException: If the record with the specified ID is not found.

    Returns:
        JSON response containing the updated record's data.
    \"\"\"
    db_obj = crud_{table.name}.get(db, {primary_key_column}={primary_key_column})
    if not db_obj:
        # Raise a 404 Not Found error if the record does not exist
        raise HTTPException(status_code=ErrorCode.NOT_FOUND.value, detail=_("{class_name} not found."))
    # Update the record with the provided data
    updated_obj = crud_{table.name}.update(
        db, db_obj=db_obj, obj_in=obj_in.model_dump(exclude_unset=True)
    )
    # Return the updated record's data as a dictionary
    return success_response(updated_obj.to_dict())
"""

    # Generate the delete endpoint
    api_code += f"""@router.delete("/delete/{{{primary_key_column}}}")
def delete_{table.name}({primary_key_column}: int, db: Session = Depends(get_db)):
    \"\"\"
    Delete a {class_name} record by its unique ID.

    Args:
        {primary_key_column} (int): The unique identifier of the {class_name} to delete.
        db (Session): Database session dependency.

    Raises:
        HTTPException: If the record with the specified ID is not found.

    Returns:
        JSON response indicating successful deletion.
    \"\"\"
    db_obj = crud_{table.name}.get(db, {primary_key_column}={primary_key_column})
    if db_obj is None:
        # Raise a 404 Not Found error if the record does not exist
        raise HTTPException(status_code=ErrorCode.NOT_FOUND.value, detail=_("{class_name} not found."))
    # Remove the record from the database
    crud_{table.name}.remove(db, {primary_key_column}={primary_key_column})
    # Return an empty success response
    return success_response({{}})
"""

    return api_code

