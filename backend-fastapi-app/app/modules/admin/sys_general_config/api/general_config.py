from typing import Optional
import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi_babel import _
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.core.security import get_current_admin
from app.modules.admin.sys_general_config.crud.sys_general_config import crud_sys_general_config
from app.modules.admin.sys_general_config.schemas.sys_general_config import SysGeneralConfigCreate, SysGeneralConfigUpdate
from app.utils.responses import success_response
from app.utils.response_handlers import ErrorCode
from app.modules.admin.sys_general_config.models.sys_general_config import SysGeneralConfig

# Initialize the API router for sys_general_config endpoints
router = APIRouter(
    prefix="/general/config", tags=["general_config"], dependencies=[Depends(get_current_admin)]
)

# Set the maximum per_page limit
MAX_PER_PAGE = 200
@router.get("")
def read_sys_general_config_list(
    page: int = 1,
    per_page: int = 10,
    search: Optional[str] = None,
    orderby: Optional[str] = None,  # Sorting field and direction, e.g., "name_asc"
    db: Session = Depends(get_db)
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
    # If per_page is -1, set it to the maximum allowed value
    if per_page == -1:
        per_page = MAX_PER_PAGE  # Set per_page to the maximum value (200)
    
    # Ensure per_page is within the allowed range
    per_page = min(per_page, MAX_PER_PAGE)

    per_page = 200
    
    # Ensure page and per_page are at least 1
    page = max(page, 1)
    
    # Retrieve paginated records with search and sorting
    items = crud_sys_general_config.get_multi(db, page=page, per_page=per_page, search=search, orderby=orderby)
    total = crud_sys_general_config.get_total(db, search=search)
    
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
def read_sys_general_config(id: int, db: Session = Depends(get_db)):
    """
    Retrieve a single SysGeneralConfig record by its unique ID.

    Args:
        id (int): The unique identifier of the SysGeneralConfig.
        db (Session): Database session dependency.

    Raises:
        HTTPException: If the record with the specified ID is not found.

    Returns:
        JSON response containing the record's data.
    """
    db_obj = crud_sys_general_config.get(db, id=id)
    if db_obj is None:
        # Raise a 404 Not Found error if the record does not exist
        raise HTTPException(status_code=ErrorCode.NOT_FOUND.value, detail=_("SysGeneralConfig not found."))
    # Return the record's data as a dictionary
    return success_response(db_obj.to_dict())
@router.post("/create")
def create_sys_general_config(obj_in: SysGeneralConfigCreate, db: Session = Depends(get_db)):
    """
    Create a new SysGeneralConfig record.

    Args:
        obj_in (SysGeneralConfigCreate): The schema containing the record's creation data.
        db (Session): Database session dependency.

    Returns:
        JSON response containing the ID of the newly created record.
    """
    ret = crud_sys_general_config.create(db, obj_in=obj_in)
    # Return the ID of the inserted record
    return success_response({"insert_id": ret.id})
@router.put("/update/{id}")
def update_sys_general_config(id: int, obj_in: SysGeneralConfigUpdate, db: Session = Depends(get_db)):
    """
    Update an existing SysGeneralConfig record.

    Args:
        id (int): The unique identifier of the SysGeneralConfig to update.
        obj_in (SysGeneralConfigUpdate): The schema containing the updated data.
        db (Session): Database session dependency.

    Raises:
        HTTPException: If the record with the specified ID is not found.

    Returns:
        JSON response containing the updated record's data.
    """
    db_obj = crud_sys_general_config.get(db, id=id)
    if not db_obj:
        # Raise a 404 Not Found error if the record does not exist
        raise HTTPException(status_code=ErrorCode.NOT_FOUND.value, detail=_("SysGeneralConfig not found."))
    # Update the record with the provided data
    updated_obj = crud_sys_general_config.update(
        db, db_obj=db_obj, obj_in=obj_in.model_dump(exclude_unset=True)
    )
    # Return the updated record's data as a dictionary
    return success_response(updated_obj.to_dict())
@router.delete("/delete/{id}")
def delete_sys_general_config(id: int, db: Session = Depends(get_db)):
    """
    Delete a SysGeneralConfig record by its unique ID.

    Args:
        id (int): The unique identifier of the SysGeneralConfig to delete.
        db (Session): Database session dependency.

    Raises:
        HTTPException: If the record with the specified ID is not found.

    Returns:
        JSON response indicating successful deletion.
    """
    db_obj = crud_sys_general_config.get(db, id=id)
    if db_obj is None:
        # Raise a 404 Not Found error if the record does not exist
        raise HTTPException(status_code=ErrorCode.NOT_FOUND.value, detail=_("SysGeneralConfig not found."))
    # Remove the record from the database
    crud_sys_general_config.remove(db, id=id)
    # Return an empty success response
    return success_response({})


@router.post("/save")
def save_general_config(
    request_data: dict,
    db: Session = Depends(get_db)
):
    """
    Save multiple general configuration values in batch.
    
    Args:
        request_data (dict): The request data containing configuration values.
            Expected format: {"row[config_name]": "value"} or 
            {"row[config_name][0][key]": "key1", "row[config_name][0][value]": "value1", ...}
        db (Session): Database session dependency.
    
    Returns:
        JSON response indicating successful save.
    """
    try:
        logger = logging.getLogger(__name__)
        logger.info(f"Received save request with {len(request_data)} items")
        
        # Parse the request data to extract configuration updates
        updates = {}
        
        # Process all request data
        for key, value in request_data.items():
            if not key.startswith("row["):
                continue
                
            # Remove "row[" prefix
            key_without_prefix = key[4:]
            
            # Check if it's a simple format: row[config_name]
            # Simple format should have no additional "][" in the key
            if key_without_prefix.endswith("]") and "][" not in key_without_prefix:
                # Simple format: row[config_name]
                config_name = key_without_prefix[:-1]  # Remove trailing "]"
                updates[config_name] = value
                logger.debug(f"Simple config: {config_name} = {value}")
                continue
            
            # Complex format: row[config_name][index][field]
            # Parse using a simpler approach
            try:
                logger.debug(f"Parsing complex key: {key}, key_without_prefix: {key_without_prefix}")
                # Find the first closing bracket after the config name
                config_end = key_without_prefix.find("]")
                if config_end == -1:
                    logger.warning(f"Invalid key format (missing ']'): {key}")
                    continue
                
                config_name = key_without_prefix[:config_end]
                remaining = key_without_prefix[config_end + 1:]  # Skip the "]"
                logger.debug(f"Extracted config_name: {config_name}, remaining: {remaining}")
                
                # Check if we have [index][field] pattern
                if not remaining.startswith("["):
                    logger.warning(f"Invalid key format (missing '[' after config): {key}")
                    continue
                
                # Remove the leading "["
                remaining = remaining[1:]
                
                # Find the next "]"
                index_end = remaining.find("]")
                if index_end == -1:
                    logger.warning(f"Invalid key format (missing ']' for index): {key}")
                    continue
                
                index_str = remaining[:index_end]
                remaining = remaining[index_end + 1:]  # Skip the "]"
                logger.debug(f"Extracted index_str: {index_str}, remaining after index: {remaining}")
                
                # Check if we have [field] pattern
                if not remaining.startswith("["):
                    logger.warning(f"Invalid key format (missing '[' for field): {key}")
                    continue
                
                # Remove the leading "["
                remaining = remaining[1:]
                
                # The rest should be the field with a trailing "]"
                if not remaining.endswith("]"):
                    logger.warning(f"Invalid key format (missing trailing ']'): {key}")
                    continue
                
                field_type = remaining[:-1]  # Remove trailing "]"
                logger.debug(f"Extracted field_type: {field_type}")
                
                # Parse index
                try:
                    idx = int(index_str)
                except ValueError:
                    logger.warning(f"Invalid index (not a number): {index_str} in key: {key}")
                    idx = 0
                
                logger.debug(f"Final parsed values: config_name={config_name}, idx={idx}, field_type={field_type}, value={value}")
                
                # Ensure config exists in updates
                if config_name not in updates:
                    updates[config_name] = []
                
                # Ensure it's a list (array config)
                if not isinstance(updates[config_name], list):
                    # If it was previously a simple value, convert to array
                    logger.warning(f"Config {config_name} was simple value, converting to array")
                    updates[config_name] = []
                
                # Ensure array is large enough
                while len(updates[config_name]) <= idx:
                    updates[config_name].append({"key": "", "value": ""})
                
                # Set the appropriate field
                if field_type == "key":
                    updates[config_name][idx]["key"] = value
                    logger.debug(f"Array config key: {config_name}[{idx}].key = {value}")
                elif field_type == "value":
                    updates[config_name][idx]["value"] = value
                    logger.debug(f"Array config value: {config_name}[{idx}].value = {value}")
                else:
                    logger.warning(f"Unknown field type: {field_type} for key: {key}")
                    
            except Exception as e:
                logger.error(f"Error parsing key {key}: {str(e)}")
                continue
        
        logger.info(f"Parsed updates for {len(updates)} config items")
        # 记录所有解析的更新
        for config_name, new_value in updates.items():
            if isinstance(new_value, list):
                logger.info(f"Config {config_name} is array with {len(new_value)} items: {new_value}")
            else:
                logger.info(f"Config {config_name} is simple value: {new_value}")
        
        # Now update the database
        updated_count = 0
        for config_name, new_value in updates.items():
            # Find the configuration by name
            config_item = db.query(SysGeneralConfig).filter(
                SysGeneralConfig.name == config_name
            ).first()
            
            if config_item:
                # Convert array values to JSON string
                if isinstance(new_value, list):
                    # Convert list of dicts to a single dict
                    value_dict = {}
                    for idx, item in enumerate(new_value):
                        # 检查key是否存在且不为空字符串
                        key = item.get("key")
                        if key is not None and key != "":
                            value = item.get("value")
                            logger.debug(f"Processing item {idx} for {config_name}: key='{key}', value='{value}'")
                            value_dict[key] = value if value is not None else ""
                    # Convert to JSON string
                    import json
                    new_value_str = json.dumps(value_dict, ensure_ascii=False)
                    logger.info(f"Converted array to JSON for {config_name}: {new_value_str}")
                    logger.debug(f"Array items: {new_value}, Result dict: {value_dict}")
                else:
                    new_value_str = str(new_value) if new_value is not None else ""
                    logger.info(f"Simple value for {config_name}: {new_value_str}")
                
                # Update the value
                config_item.value = new_value_str
                db.add(config_item)
                updated_count += 1
                logger.info(f"Updated config {config_name} with value: {new_value_str}")
            else:
                logger.warning(f"Config item not found: {config_name}")
        
        # Commit all changes
        db.commit()
        logger.info(f"Successfully updated {updated_count} config items")
        
        return success_response({"message": _("Configuration saved successfully")})
    
    except Exception as e:
        db.rollback()
        logger = logging.getLogger(__name__)
        logger.error(f"Error saving general config: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=_("Failed to save configuration: {error}").format(error=str(e))
        )
