import os

from fastapi import APIRouter, Depends, HTTPException
from fastapi_babel import _
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_current_admin
from app.dependencies.database import get_db
from app.modules.admin.sys_attachment.crud.sys_attachment import crud_sys_attachment
from app.modules.admin.sys_attachment.schemas.sys_attachment import (
    SysAttachmentCreate,
    SysAttachmentUpdate,
)
from app.modules.admin.sys_attachment_category.crud.sys_attachment_category import (
    crud_sys_attachment_category,
)
from app.utils.log_utils import logger
from app.utils.response_handlers import ErrorCode
from app.utils.responses import success_response


def safe_delete_file(file_path: str) -> bool:
    """
    安全删除文件，防止路径遍历攻击

    Args:
        file_path: 文件路径（可以是相对路径或绝对路径）

    Returns:
        bool: 是否成功删除文件（如果文件不存在也返回True）

    Raises:
        HTTPException: 如果检测到路径遍历攻击
    """
    try:
        # 获取上传目录的绝对路径
        upload_dir = os.path.abspath(settings.UPLOAD_DIR)

        # 处理文件路径
        if os.path.isabs(file_path):
            # 如果是绝对路径，确保它在UPLOAD_DIR内
            abs_path = os.path.abspath(file_path)
        else:
            # 如果是相对路径，转换为基于UPLOAD_DIR的绝对路径
            abs_path = os.path.abspath(os.path.join(upload_dir, file_path))

        # 安全检查：确保文件路径在UPLOAD_DIR内
        if not abs_path.startswith(upload_dir):
            logger.warning("尝试删除UPLOAD_DIR之外的文件: {abs_path}")
            raise HTTPException(status_code=400, detail="无效的文件路径")

        # 检查文件是否存在
        if not os.path.exists(abs_path):
            logger.info("文件不存在，跳过删除: {abs_path}")
            return True

        # 删除文件
        os.remove(abs_path)
        logger.info("成功删除文件: {abs_path}")

        # 尝试删除空目录（最多向上追溯3级）
        current_dir = os.path.dirname(abs_path)
        for _ in range(3):
            if current_dir == upload_dir or not current_dir.startswith(upload_dir):
                break
            try:
                if os.path.exists(current_dir) and not os.listdir(current_dir):
                    os.rmdir(current_dir)
                    logger.info("删除空目录: {current_dir}")
                    current_dir = os.path.dirname(current_dir)
                else:
                    break
            except Exception:
                logger.debug("无法删除目录 {current_dir}: {e}")
                break

        return True

    except HTTPException:
        raise
    except Exception:
        logger.error("删除文件失败 {file_path}: {e}")
        return False


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
    search: str | None = None,
    orderby: str | None = "id_desc",  # Sorting field and direction, e.g., "name_asc"
    db: Session = Depends(get_db),
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
    items = crud_sys_attachment.get_multi(
        db, page=page, per_page=per_page, search=search, orderby=orderby
    )
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
            item_dict["cat_name"] = category_map[item.cat_id]
        else:
            item_dict["cat_name"] = None
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
        raise HTTPException(
            status_code=ErrorCode.NOT_FOUND.value, detail=_("SysAttachment not found.")
        )
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
        raise HTTPException(
            status_code=ErrorCode.NOT_FOUND.value, detail=_("SysAttachment not found.")
        )
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
        raise HTTPException(
            status_code=ErrorCode.NOT_FOUND.value, detail=_("SysAttachment not found.")
        )

    # 获取文件路径
    file_path = db_obj.path_file
    if file_path:
        try:
            # 安全删除物理文件
            safe_delete_file(file_path)
        except HTTPException:
            # 如果文件删除出现安全问题，仍然继续删除数据库记录
            logger.warning("文件删除安全检查失败，继续删除数据库记录: {e}")
        except Exception:
            # 文件删除失败，记录错误但继续删除数据库记录
            logger.error("删除物理文件失败，继续删除数据库记录: {e}")

    # 删除数据库记录
    crud_sys_attachment.remove(db, id=id)

    # 返回成功响应
    return success_response({})
