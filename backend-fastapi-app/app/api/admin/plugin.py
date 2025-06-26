import json
from pathlib import Path
import re
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi_babel import _
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.crud.sys_plugin import crud_sys_plugin
from app.schemas.sys_plugin import SysPluginCreate, SysPluginUpdate
from app.utils.responses import success_response
from app.utils.response_handlers import ErrorCode
from app.models.sys_plugin import SysPlugin as SysPluginModel
from app.core.security import get_current_admin

from app.utils.log_utils import logger
from app.core.config import settings 
from app.core.plugin_loader import PluginLoader

# Initialize the API router for sys_plugin endpoints
router = APIRouter(
    prefix="/plugin", tags=["plugin"]
)

# Set the maximum per_page limit
MAX_PER_PAGE = 200

plugin_loader = PluginLoader(Path(settings.PLUGINS_DIR))


@router.get("/plugins_list")
async def list_plugins(request: Request):
    try:
        app = request.app
        plugins_dir = Path(settings.PLUGINS_DIR)
        for plugin_path in plugins_dir.iterdir():
            if plugin_path.is_dir():
                await plugin_loader._load_plugin(plugin_path, app)
        plugins = plugin_loader.list_plugins()
        
        logger.info(f"插件列表获取成功，包含 {len(plugins)} 个插件")
        return success_response(plugins) 
    except Exception as e:
        logger.error(f"获取插件列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取插件列表失败: {str(e)}")

@router.get("/plugins/{plugin_id}/manifest.json")
async def get_plugin_remote_entry(plugin_id: str):
    """
    获取插件的 manifest.json 文件
    """
    try:
        # 检查插件是否存在
        plugin_dir = Path(settings.PLUGINS_DIR) / plugin_id
        if not plugin_dir.exists():
            logger.warning(f"插件目录不存在: {plugin_dir}")
            raise HTTPException(status_code=404, detail="插件不存在")
        
        # 检查 manifest.json 文件是否存在
        remote_entry_path = plugin_dir / "manifest.json"
        if not remote_entry_path.exists():
            logger.warning(f"manifest.json 文件不存在: {remote_entry_path}")
            raise HTTPException(status_code=404, detail="manifest.json 文件不存在")
        
        # 返回 manifest.json 文件
        return FileResponse(remote_entry_path, media_type="application/javascript")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取 manifest.json 文件失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取 manifest.json 文件失败: {str(e)}")

@router.get("/plugins/{plugin_id}/remoteEntry.js")
async def get_plugin_remote_entry(plugin_id: str):
    """
    获取插件的 remoteEntry.js 文件
    """
    try:
        # 检查插件是否存在
        plugin_dir =  Path(settings.PLUGINS_DIR) / plugin_id
        if not plugin_dir.exists():
            logger.warning(f"插件目录不存在: {plugin_dir}")
            raise HTTPException(status_code=404, detail="插件不存在")
        
        # 检查 remoteEntry.js 文件是否存在
        remote_entry_path = plugin_dir / "remoteEntry.js"
        if not remote_entry_path.exists():
            logger.warning(f"remoteEntry.js 文件不存在: {remote_entry_path}")
            raise HTTPException(status_code=404, detail="remoteEntry.js 文件不存在")
        
        # 返回 remoteEntry.js 文件
        return FileResponse(remote_entry_path, media_type="application/javascript")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取 remoteEntry.js 文件失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取 remoteEntry.js 文件失败: {str(e)}")


@router.get("/plugins/{plugin_id}/component/{component_name}")
async def get_plugin_component(plugin_id: str, component_name: str):
    """
    获取插件组件
    """
    try:
        # 检查插件是否存在
        plugin_dir = Path(settings.PLUGINS_DIR) / plugin_id
        if not plugin_dir.exists():
            logger.warning(f"插件目录不存在: {plugin_dir}")
            raise HTTPException(status_code=404, detail="插件不存在")
        
        # 尝试从插件目录加载组件文件
        component_path = plugin_dir / "frontend" / "components" / f"{component_name}.vue"
        if component_path.exists():
            # 读取组件文件内容
            component_content = component_path.read_text()
            logger.info(f"从文件加载组件: {component_path}")
            
            # 简单处理：提取<template>和<script>部分
            template_match = re.search(r'<template>(.*?)</template>', component_content, re.DOTALL)
            script_match = re.search(r'<script>(.*?)</script>', component_content, re.DOTALL)
            
            template = template_match.group(1) if template_match else ""
            script = script_match.group(1) if script_match else ""
            
            # 返回组件渲染函数
            return success_response({
                "template": template,
                "script": script,
                "render": f"function(h) {{ return h('div', {{ class: 'plugin-component' }}, [ h('h2', '{component_name}'), h('div', {{ class: 'component-content' }}, '组件内容从文件加载') ]); }}"
            }) 
        
        # 如果找不到组件文件，尝试从manifest中获取组件信息
        manifest_path = plugin_dir / "manifest.json"
        if manifest_path.exists():
            manifest = json.loads(manifest_path.read_text())
            components = manifest.get("component", []) or manifest.get("components", [])
            
            if component_name in components:
                # 返回基于组件名的默认实现
                logger.info(f"从manifest生成组件: {component_name}")
                return {
                    "render": f"function(h) {{ return h('div', {{ class: 'plugin-component' }}, [ h('h2', '{component_name}'), h('div', {{ class: 'component-content' }}, '组件 {component_name} 的默认实现') ]); }}"
                }
        
        # 返回默认组件
        logger.warning(f"未知组件: {component_name}")
        return {
            "render": f"function(h) {{ return h('div', {{ class: 'error-component' }}, [ h('h2', '未知组件'), h('p', '组件不存在: {component_name}') ]); }}"
        }
        
        logger.info(f"成功获取插件组件: {plugin_id}/{component_name}")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取插件组件失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取组件失败: {str(e)}")

@router.get("/list")
def read_sys_plugin_list(
    page: int = 1,
    per_page: int = 10,
    search: Optional[str] = None,
    orderby: Optional[str] = None,  # Sorting field and direction, e.g., "name_asc"
    db: Session = Depends(get_db),
):
    """
    Retrieve a list of SysPlugin records with optional pagination, search, and sorting.

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
    items = crud_sys_plugin.get_multi(
        db, page=page, per_page=per_page, search=search, orderby=orderby
    )
    total = crud_sys_plugin.get_total(db, search=search)

    response_page = page
    response_per_page = per_page

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


@router.get("/{id}")
def read_sys_plugin(id: int, db: Session = Depends(get_db)):
    """
    Retrieve a single SysPlugin record by its unique ID.

    Args:
        id (int): The unique identifier of the SysPlugin.
        db (Session): Database session dependency.

    Raises:
        HTTPException: If the record with the specified ID is not found.

    Returns:
        JSON response containing the record's data.
    """
    db_obj = crud_sys_plugin.get(db, id=id)
    if db_obj is None:
        # Raise a 404 Not Found error if the record does not exist
        raise HTTPException(
            status_code=ErrorCode.NOT_FOUND.value, detail=_("SysPlugin not found.")
        )
    # Return the record's data as a dictionary
    return success_response(db_obj.to_dict())


@router.post("/create")
def create_sys_plugin(obj_in: SysPluginCreate, db: Session = Depends(get_db)):
    """
    Create a new SysPlugin record.

    Args:
        obj_in (SysPluginCreate): The schema containing the record's creation data.
        db (Session): Database session dependency.

    Returns:
        JSON response containing the ID of the newly created record.
    """
    ret = crud_sys_plugin.create(db, obj_in=obj_in)
    # Return the ID of the inserted record
    return success_response({"insert_id": ret.id})


@router.put("/update/{id}")
def update_sys_plugin(id: int, obj_in: SysPluginUpdate, db: Session = Depends(get_db)):
    """
    Update an existing SysPlugin record.

    Args:
        id (int): The unique identifier of the SysPlugin to update.
        obj_in (SysPluginUpdate): The schema containing the updated data.
        db (Session): Database session dependency.

    Raises:
        HTTPException: If the record with the specified ID is not found.

    Returns:
        JSON response containing the updated record's data.
    """
    db_obj = crud_sys_plugin.get(db, id=id)
    if not db_obj:
        # Raise a 404 Not Found error if the record does not exist
        raise HTTPException(
            status_code=ErrorCode.NOT_FOUND.value, detail=_("SysPlugin not found.")
        )
    # Update the record with the provided data
    updated_obj = crud_sys_plugin.update(
        db, db_obj=db_obj, obj_in=obj_in.model_dump(exclude_unset=True)
    )
    # Return the updated record's data as a dictionary
    return success_response(updated_obj.to_dict())


@router.delete("/delete/{id}")
def delete_sys_plugin(id: int, db: Session = Depends(get_db)):
    """
    Delete a SysPlugin record by its unique ID.

    Args:
        id (int): The unique identifier of the SysPlugin to delete.
        db (Session): Database session dependency.

    Raises:
        HTTPException: If the record with the specified ID is not found.

    Returns:
        JSON response indicating successful deletion.
    """
    db_obj = crud_sys_plugin.get(db, id=id)
    if db_obj is None:
        # Raise a 404 Not Found error if the record does not exist
        raise HTTPException(
            status_code=ErrorCode.NOT_FOUND.value, detail=_("SysPlugin not found.")
        )
    # Remove the record from the database
    crud_sys_plugin.remove(db, id=id)
    # Return an empty success response
    return success_response({})
