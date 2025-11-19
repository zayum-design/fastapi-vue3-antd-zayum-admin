from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi_babel import _
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.core.security import get_current_admin
from app.crud.sys_attachment import crud_sys_attachment
from app.crud.sys_attachment_category import crud_sys_attachment_category
from app.schemas.sys_attachment import SysAttachmentCreate, SysAttachmentUpdate
from app.utils.responses import success_response
from app.utils.response_handlers import ErrorCode
from app.models.sys_attachment import SysAttachment as SysAttachmentModel

# Initialize the API router for sys_attachment endpoints
router = APIRouter(
    prefix="/attachment", tags=["attachment"], dependencies=[Depends(get_current_admin)]
)

# Set the maximum per_page limit
MAX_PER_PAGE = 200
@router.get("/list")
def read_sys_attachment_list(
    page: int = 1,
    per_page: int = 10,
    search: Optional[str] = None,
    orderby: Optional[str] = 'id_desc',  # Sorting field and direction, e.g., "name_asc"
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of SysAttachment records with optional pagination, search, and sorting.

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
    items = crud_sys_attachment.get_multi(db, page=page, per_page=per_page, search=search, orderby=orderby)
    total = crud_sys_attachment.get_total(db, search=search)
    
    response_page = page
    response_per_page = per_page

    # Get all attachment categories for name mapping
    all_categories = crud_sys_attachment_category.get_all(db)
    category_map = {category.id: category.name for category in all_categories}

    # Prepare the response data with category names
    items_with_category_names = []
    for item in items:
        item_dict = item.to_dict()
        # Add category name if cat_id exists
        if item.cat_id and item.cat_id in category_map:
            item_dict['cat_name'] = category_map[item.cat_id]
        else:
            item_dict['cat_name'] = None
        items_with_category_names.append(item_dict)

    # Prepare the response data
    return success_response(
        {
            "items": items_with_category_names,
            "total": total,
            "page": response_page,
            "per_page": response_per_page,
        }
    )
@router.get("/{id}")
def read_sys_attachment(id: int, db: Session = Depends(get_db)):
    """
    Retrieve a single SysAttachment record by its unique ID.

    Args:
        id (int): The unique identifier of the SysAttachment.
        db (Session): Database session dependency.

    Raises:
        HTTPException: If the record with the specified ID is not found.

    Returns:
        JSON response containing the record's data.
    """
    db_obj = crud_sys_attachment.get(db, id=id)
    if db_obj is None:
        # Raise a 404 Not Found error if the record does not exist
        raise HTTPException(status_code=ErrorCode.NOT_FOUND.value, detail=_("SysAttachment not found."))
    # Return the record's data as a dictionary
    return success_response(db_obj.to_dict())
@router.post("/create")
def create_sys_attachment(obj_in: SysAttachmentCreate, db: Session = Depends(get_db)):
    """
    Create a new SysAttachment record.

    Args:
        obj_in (SysAttachmentCreate): The schema containing the record's creation data.
        db (Session): Database session dependency.

    Returns:
        JSON response containing the ID of the newly created record.
    """
    ret = crud_sys_attachment.create(db, obj_in=obj_in)
    # Return the ID of the inserted record
    return success_response({"insert_id": ret.id})
@router.put("/update/{id}")
def update_sys_attachment(id: int, obj_in: SysAttachmentUpdate, db: Session = Depends(get_db)):
    """
    Update an existing SysAttachment record.

    Args:
        id (int): The unique identifier of the SysAttachment to update.
        obj_in (SysAttachmentUpdate): The schema containing the updated data.
        db (Session): Database session dependency.

    Raises:
        HTTPException: If the record with the specified ID is not found.

    Returns:
        JSON response containing the updated record's data.
    """
    db_obj = crud_sys_attachment.get(db, id=id)
    if not db_obj:
        # Raise a 404 Not Found error if the record does not exist
        raise HTTPException(status_code=ErrorCode.NOT_FOUND.value, detail=_("SysAttachment not found."))
    # Update the record with the provided data
    updated_obj = crud_sys_attachment.update(
        db, db_obj=db_obj, obj_in=obj_in.model_dump(exclude_unset=True)
    )
    # Return the updated record's data as a dictionary
    return success_response(updated_obj.to_dict())
@router.delete("/delete/{id}")
def delete_sys_attachment(id: int, db: Session = Depends(get_db)):
    """
    Delete a SysAttachment record by its unique ID.

    Args:
        id (int): The unique identifier of the SysAttachment to delete.
        db (Session): Database session dependency.

    Raises:
        HTTPException: If the record with the specified ID is not found.

    Returns:
        JSON response indicating successful deletion.
    """
    db_obj = crud_sys_attachment.get(db, id=id)
    if db_obj is None:
        # Raise a 404 Not Found error if the record does not exist
        raise HTTPException(status_code=ErrorCode.NOT_FOUND.value, detail=_("SysAttachment not found."))
    # Remove the record from the database
    crud_sys_attachment.remove(db, id=id)
    # Return an empty success response
    return success_response({})
