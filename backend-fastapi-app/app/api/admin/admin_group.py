from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi_babel import _
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.core.security import get_current_admin
from app.crud.sys_admin_group import crud_sys_admin_group
from app.schemas.sys_admin_group import SysAdminGroupCreate, SysAdminGroupUpdate
from app.utils.responses import success_response
from app.utils.response_handlers import ErrorCode
from app.models.sys_admin_group import SysAdminGroup as SysAdminGroupModel

# Initialize the API router for sys_admin_group endpoints
router = APIRouter(
    prefix="/admin/group", tags=["admin_group"], dependencies=[Depends(get_current_admin)]
)

# Set the maximum per_page limit
MAX_PER_PAGE = 200
@router.get("/list")
def read_sys_admin_group_list(
    page: int = 1,
    per_page: int = 10,
    search: Optional[str] = None,
    orderby: Optional[str] = None,  # Sorting field and direction, e.g., "name_asc"
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of SysAdminGroup records with optional pagination, search, and sorting.

    Args:
        page (int, optional): The page number to retrieve. Defaults to 1.
        per_page (int, optional): Number of records per page. Use -1 to retrieve all records. Defaults to 10.
        search (str, optional): A search string to filter records by relevant fields.
        orderby (str, optional): Sorting rule, e.g., "field_asc" or "field_desc".
        db (Session): Database session dependency.

    Returns:
        JSON response containing the list of records, total count, current page, and records per page.
    """
    # If per_page is -1, set it to the maximum allowed value
    if per_page == -1:
        per_page = MAX_PER_PAGE  # Set per_page to the maximum value (200)
    
    # Ensure per_page is within the allowed range
    per_page = min(per_page, MAX_PER_PAGE)
    
    # Ensure page and per_page are at least 1
    page = max(page, 1)
    
    # Retrieve paginated records with search and sorting
    items = crud_sys_admin_group.get_multi(db, page=page, per_page=per_page, search=search, orderby=orderby)
    total = crud_sys_admin_group.get_total(db, search=search)
    
    response_page = page
    response_per_page = per_page

    # Prepare the response data
    return success_response(
        {
            "items": [item.to_dict() for item in items],  # Convert each model instance to a dictionary
            "total": total,
            "page": response_page,
            "per_page": response_per_page,
        }
    )
@router.get("/{id}")
def read_sys_admin_group(id: int, db: Session = Depends(get_db)):
    """
    Retrieve a single SysAdminGroup record by its unique ID.

    Args:
        id (int): The unique identifier of the SysAdminGroup.
        db (Session): Database session dependency.

    Raises:
        HTTPException: If the record with the specified ID is not found.

    Returns:
        JSON response containing the record's data.
    """
    db_obj = crud_sys_admin_group.get(db, id=id)
    if db_obj is None:
        # Raise a 404 Not Found error if the record does not exist
        raise HTTPException(status_code=ErrorCode.NOT_FOUND.value, detail=_("SysAdminGroup not found."))
    # Return the record's data as a dictionary
    return success_response(db_obj.to_dict())
@router.post("/create")
def create_sys_admin_group(obj_in: SysAdminGroupCreate, db: Session = Depends(get_db)):
    """
    Create a new SysAdminGroup record.

    Args:
        obj_in (SysAdminGroupCreate): The schema containing the record's creation data.
        db (Session): Database session dependency.

    Returns:
        JSON response containing the ID of the newly created record.
    """
    ret = crud_sys_admin_group.create(db, obj_in=obj_in)
    # Return the ID of the inserted record
    return success_response({"insert_id": ret.id})
@router.put("/update/{id}")
def update_sys_admin_group(id: int, obj_in: SysAdminGroupUpdate, db: Session = Depends(get_db)):
    """
    Update an existing SysAdminGroup record.

    Args:
        id (int): The unique identifier of the SysAdminGroup to update.
        obj_in (SysAdminGroupUpdate): The schema containing the updated data.
        db (Session): Database session dependency.

    Raises:
        HTTPException: If the record with the specified ID is not found.

    Returns:
        JSON response containing the updated record's data.
    """
    db_obj = crud_sys_admin_group.get(db, id=id)
    if not db_obj:
        # Raise a 404 Not Found error if the record does not exist
        raise HTTPException(status_code=ErrorCode.NOT_FOUND.value, detail=_("SysAdminGroup not found."))
    # Update the record with the provided data
    updated_obj = crud_sys_admin_group.update(
        db, db_obj=db_obj, obj_in=obj_in.model_dump(exclude_unset=True)
    )
    # Return the updated record's data as a dictionary
    return success_response(updated_obj.to_dict())
@router.delete("/delete/{id}")
def delete_sys_admin_group(id: int, db: Session = Depends(get_db)):
    """
    Delete a SysAdminGroup record by its unique ID.

    Args:
        id (int): The unique identifier of the SysAdminGroup to delete.
        db (Session): Database session dependency.

    Raises:
        HTTPException: If the record with the specified ID is not found.

    Returns:
        JSON response indicating successful deletion.
    """
    db_obj = crud_sys_admin_group.get(db, id=id)
    if db_obj is None:
        # Raise a 404 Not Found error if the record does not exist
        raise HTTPException(status_code=ErrorCode.NOT_FOUND.value, detail=_("SysAdminGroup not found."))
    # Remove the record from the database
    crud_sys_admin_group.remove(db, id=id)
    # Return an empty success response
    return success_response({})
