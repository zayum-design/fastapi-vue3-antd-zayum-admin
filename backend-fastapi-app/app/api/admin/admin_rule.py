from collections import defaultdict
from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi_babel import _
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.crud.sys_admin_rule import crud_sys_admin_rule
from app.schemas.sys_admin_rule import (
    SysAdminRule,
    SysAdminRuleCreate,
    SysAdminRuleTree,
    SysAdminRuleUpdate,
)
from app.utils.responses import success_response
from app.utils.response_handlers import ErrorCode
from app.core.security import get_current_admin

# Initialize the API router for sys_admin_rule endpoints
router = APIRouter(
    prefix="/admin/rule", tags=["admin_rule"], dependencies=[Depends(get_current_admin)]
)

# Set the maximum per_page limit
MAX_PER_PAGE = 200


@router.get("/list")
def read_sys_admin_rule_list(
    page: int = 1,
    per_page: int = 10,
    search: Optional[str] = None,
    orderby: Optional[str] = None,  # Sorting field and direction, e.g., "name_asc"
    db: Session = Depends(get_db),
):
    """
    Retrieve a list of SysAdminRule records with optional pagination, search, and sorting.

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
    items = crud_sys_admin_rule.get_multi(
        db, page=page, per_page=per_page, search=search, orderby=orderby
    )

    items = build_tree(items)
    # Prepare the response data

    total = crud_sys_admin_rule.get_total(db, search=search)

    response_page = page
    response_per_page = per_page

    # Prepare the response data
    return success_response(
        {
            "items": items,  # Convert each model instance to a dictionary
            "total": total,
            "page": response_page,
            "per_page": response_per_page,
        }
    )


from typing import List, Dict, Optional
from collections import defaultdict
from app.models.sys_admin_rule import SysAdminRule as ModelSysAdminRule


def build_tree(items: List[ModelSysAdminRule]) -> List[Dict]:
    """
    将平面的 SysAdminRule 列表转换为树形结构，去除没有子节点的 children 字段
    """
    # 预处理items，确保permission字段是字典类型
    for item in items:
        if hasattr(item, 'permission') and isinstance(item.permission, str):
            try:
                item.permission = {} if item.permission == '{}' else eval(item.permission)
            except:
                item.permission = {}
    
    # 将 SQLAlchemy 对象转换为 Pydantic 对象
    pydantic_items = [SysAdminRuleTree.from_orm(item) for item in items]

    # 创建一个 id 到节点的映射
    item_dict: Dict[int, SysAdminRuleTree] = {item.id: item for item in pydantic_items}

    # 创建 parent_id 到子节点的映射
    children_map: Dict[int, List[SysAdminRuleTree]] = defaultdict(list)
    for item in pydantic_items:
        parent_id = item.parent_id if item.parent_id is not None else 0
        children_map[parent_id].append(item)

    # 递归地将子节点添加到父节点的 children 字段中
    def add_children(item: SysAdminRuleTree):
        children = children_map.get(item.id, [])
        if children:  # 如果有子节点，递归添加子节点
            item.children = []
            for child in children:
                add_children(child)
                item.children.append(child)
        else:  # 如果没有子节点，设置为空列表
            item.children = []

    # 提取顶级节点（parent_id=0）
    tree = children_map.get(0, [])

    # 递归处理所有顶级节点及其子节点
    for item in tree:
        add_children(item)

    # 将树结构转换成字典格式，去除空的children字段
    def convert_to_dict(item: SysAdminRuleTree) -> Dict:
        result = item.dict()  # 转换为字典
        # 如果children为空（为None或为空列表），删除该字段
        if item.children is None or len(item.children) == 0:
            result.pop("children", None)
        return result

    # 将树结构转换并返回，去除没有子节点的children字段
    return [convert_to_dict(item) for item in tree]


@router.get("/{id}")
def read_sys_admin_rule(id: int, db: Session = Depends(get_db)):
    """
    Retrieve a single SysAdminRule record by its unique ID.

    Args:
        id (int): The unique identifier of the SysAdminRule.
        db (Session): Database session dependency.

    Raises:
        HTTPException: If the record with the specified ID is not found.

    Returns:
        JSON response containing the record's data.
    """
    db_obj = crud_sys_admin_rule.get(db, id=id)
    if db_obj is None:
        # Raise a 404 Not Found error if the record does not exist
        raise HTTPException(
            status_code=ErrorCode.NOT_FOUND.value, detail=_("SysAdminRule not found.")
        )
    # Return the record's data as a dictionary
    return success_response(db_obj.to_dict())


@router.post("/create")
def create_sys_admin_rule(obj_in: SysAdminRuleCreate, db: Session = Depends(get_db)):
    """
    Create a new SysAdminRule record.

    Args:
        obj_in (SysAdminRuleCreate): The schema containing the record's creation data.
        db (Session): Database session dependency.

    Returns:
        JSON response containing the ID of the newly created record.
    """
    ret = crud_sys_admin_rule.create(db, obj_in=obj_in)
    # Return the ID of the inserted record
    return success_response({"insert_id": ret.id})


@router.put("/update/{id}")
def update_sys_admin_rule(
    id: int, obj_in: SysAdminRuleUpdate, db: Session = Depends(get_db)
):
    """
    Update an existing SysAdminRule record.

    Args:
        id (int): The unique identifier of the SysAdminRule to update.
        obj_in (SysAdminRuleUpdate): The schema containing the updated data.
        db (Session): Database session dependency.

    Raises:
        HTTPException: If the record with the specified ID is not found.

    Returns:
        JSON response containing the updated record's data.
    """
    db_obj = crud_sys_admin_rule.get(db, id=id)
    if not db_obj:
        # Raise a 404 Not Found error if the record does not exist
        raise HTTPException(
            status_code=ErrorCode.NOT_FOUND.value, detail=_("SysAdminRule not found.")
        )
    # Update the record with the provided data
    updated_obj = crud_sys_admin_rule.update(
        db, db_obj=db_obj, obj_in=obj_in.model_dump(exclude_unset=True)
    )
    # Return the updated record's data as a dictionary
    return success_response(updated_obj.to_dict())


@router.delete("/delete/{id}")
def delete_sys_admin_rule(id: int, db: Session = Depends(get_db)):
    """
    Delete a SysAdminRule record by its unique ID.

    Args:
        id (int): The unique identifier of the SysAdminRule to delete.
        db (Session): Database session dependency.

    Raises:
        HTTPException: If the record with the specified ID is not found.

    Returns:
        JSON response indicating successful deletion.
    """
    db_obj = crud_sys_admin_rule.get(db, id=id)
    if db_obj is None:
        # Raise a 404 Not Found error if the record does not exist
        raise HTTPException(
            status_code=ErrorCode.NOT_FOUND.value, detail=_("SysAdminRule not found.")
        )
    # Remove the record from the database
    crud_sys_admin_rule.remove(db, id=id)
    # Return an empty success response
    return success_response({})
