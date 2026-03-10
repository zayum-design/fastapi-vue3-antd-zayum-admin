from fastapi import APIRouter, Depends, HTTPException
from fastapi_babel import _
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.dependencies.database import get_db
from app.modules.admin.sys_user_score_log.crud.sys_user_score_log import (
    crud_sys_user_score_log,
)
from app.modules.admin.sys_user.models.sys_user import SysUser
from app.utils.response_handlers import ErrorCode
from app.utils.responses import success_response

# Initialize the API router for user score log endpoints
router = APIRouter(
    prefix="/score/log", tags=["user_score_log"], dependencies=[Depends(get_current_user)]
)

# Set the maximum per_page limit
MAX_PER_PAGE = 200


@router.get("/list")
def read_user_score_log_list(
    page: int = 1,
    per_page: int = 10,
    search: str | None = None,
    orderby: str | None = None,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """
    Retrieve a list of current user's score log records with optional pagination, search, and sorting.

    Args:
        page (int, optional): The page number to retrieve. Defaults to 1.
        per_page (int, optional): Number of records per page. Use -1 to retrieve all records. Defaults to 10.
        search (str, optional): A search string to filter records by relevant fields.
        orderby (str, optional): Sorting rule, e.g., "field_asc" or "field_desc".
        db (Session): Database session dependency.
        current_user (SysUser): Current logged-in user.

    Returns:
        JSON response containing the list of records, total count, current page, and records per page.
    """
    # If per_page is -1, set it to the maximum allowed value
    if per_page == -1:
        per_page = MAX_PER_PAGE

    # Ensure per_page is within the allowed range
    per_page = min(per_page, MAX_PER_PAGE)

    # Ensure page and per_page are at least 1
    page = max(page, 1)

    # Filter by current user's ID
    from app.modules.admin.sys_user_score_log.models.sys_user_score_log import SysUserScoreLog
    base_query = db.query(SysUserScoreLog).filter(SysUserScoreLog.user_id == current_user.id)

    # Retrieve paginated records with search and sorting
    items = crud_sys_user_score_log.get_multi(
        db, page=page, per_page=per_page, search=search, orderby=orderby, base_query=base_query
    )
    total = crud_sys_user_score_log.get_total(db, search=search, base_query=base_query)

    response_page = page
    response_per_page = per_page

    # Prepare the response data
    return success_response(
        {
            "items": [
                item.to_dict() for item in items
            ],
            "total": total,
            "page": response_page,
            "per_page": response_per_page,
        }
    )


@router.get("/{id}")
def read_user_score_log(
    id: int, 
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """
    Retrieve a single score log record by its unique ID.
    Only returns the record if it belongs to the current user.

    Args:
        id (int): The unique identifier of the score log.
        db (Session): Database session dependency.
        current_user (SysUser): Current logged-in user.

    Raises:
        HTTPException: If the record with the specified ID is not found or doesn't belong to current user.

    Returns:
        JSON response containing the record's data.
    """
    db_obj = crud_sys_user_score_log.get(db, id=id)
    if db_obj is None:
        raise HTTPException(
            status_code=ErrorCode.NOT_FOUND.value, detail=_("Score log not found.")
        )
    
    # Check if the record belongs to the current user
    if db_obj.user_id != current_user.id:
        raise HTTPException(
            status_code=ErrorCode.FORBIDDEN.value, detail=_("Access denied.")
        )
    
    return success_response(db_obj.to_dict())
