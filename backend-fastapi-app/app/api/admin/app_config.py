from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi_babel import _
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.crud.sys_general_config import crud_sys_general_config
from app.schemas.sys_general_config import (
    SysGeneralConfigCreate,
    SysGeneralConfigUpdate,
)
from app.utils.responses import success_response
from app.utils.response_handlers import ErrorCode
from app.models.sys_general_config import SysGeneralConfig as SysGeneralConfigModel
from app.core.security import get_current_admin

# Initialize the API router for sys_general_config endpoints
router = APIRouter(
    prefix="/admin/config",
    tags=["admin_config"],
    dependencies=[Depends(get_current_admin)],
)


@router.get("")
def read_sys_general_config_list(
    page: int = 1,
    per_page: int = 10,
    search: Optional[str] = None,
    orderby: Optional[str] = None,  # Sorting field and direction, e.g., "name_asc"
    db: Session = Depends(get_db),
):
    """
    Retrieve a list of SysGeneralConfig records with optional pagination, search, and sorting.

    Args:
        page (int, optional): The page number to retrieve. Defaults to 1.
        per_page (int, optional): Number of records per page. Use -1 to retrieve all records. Defaults to 10.
        search (str, optional): A search string to filter records by relevant fields.
        orderby (str, optional): Sorting rule, e.g., "field_asc" or "field_desc".
        db (Session): Database session dependency.

    Returns:
        JSON response containing the list of records, total count, current page, and records per page.
    """

    # Retrieve all records without pagination
    items = crud_sys_general_config.get_all(db, search=search, orderby=orderby)
    total = len(items)
    response_page = 1
    response_per_page = total
    # Prepare the response data
    return success_response(
        {
            "items": [
                item.to_dict() for item in items
            ],  # Convert each model instance to a dictionary
            "total": total,
            "page": response_page,
            "per_page": response_per_page,
        }
    )
