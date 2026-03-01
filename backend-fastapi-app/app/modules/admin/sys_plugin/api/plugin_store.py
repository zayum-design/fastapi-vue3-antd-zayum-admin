import json
from pathlib import Path
import re
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi_babel import _
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.modules.admin.sys_plugin.crud.sys_plugin import crud_sys_plugin
from app.modules.admin.sys_plugin.schemas.sys_plugin import SysPluginCreate, SysPluginUpdate
from app.utils.responses import success_response
from app.utils.response_handlers import ErrorCode
from app.modules.admin.sys_plugin.models.sys_plugin import SysPlugin as SysPluginModel
from app.core.security import get_current_admin

from app.utils.log_utils import logger
from app.core.config import settings 
from app.core.plugin_loader import PluginLoader

# Initialize the API router for sys_plugin endpoints
router = APIRouter(
    prefix="/plugin_store", tags=["plugin_store"]
)

# Set the maximum per_page limit
MAX_PER_PAGE = 200

# 使用 settings.PLUGINS_DIR 作为插件目录
plugins_dir_path = Path(settings.PLUGINS_DIR)
plugin_loader = PluginLoader(plugins_dir_path)

@router.get("/list")
async def read_sys_plugin_list(
    request: Request,
    page: int = 1,
    per_page: int = 10,
    search: Optional[str] = None,
    orderby: Optional[str] = None,  # Sorting field and direction, e.g., "name_asc"
    type: str = "all",  # all, store, local
    db: Session = Depends(get_db),
):
    """
    Retrieve a list of SysPlugin records with optional pagination, search, and sorting.

    Args:
        page (int, optional): The page number to retrieve. Defaults to 1.
        per_page (int, optional): Number of records per page. Use -1 to retrieve all records. Defaults to 10.
        search (str, optional): A search string to filter records by relevant fields.
        orderby (str, optional): Sorting rule, e.g., "field_asc" or "field_desc".
        type (str, optional): Plugin type filter: "all" (store + local), "store" (database only), "local" (local plugins only). Defaults to "all".
        db (Session): Database session dependency.
        request (Request): FastAPI request object.

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

    # Validate type parameter
    if type not in ["all", "store", "local"]:
        type = "all"

    # Get store plugins (from database)
    store_items = []
    store_total = 0
    if type in ["all", "store"]:
        store_items = crud_sys_plugin.get_multi(
            db, page=page, per_page=per_page, search=search, orderby=orderby
        )
        store_total = crud_sys_plugin.get_total(db, search=search)

    # Get local plugins
    local_items = []
    local_total = 0
    if type in ["all", "local"]:
        try:
            # Load local plugins
            app = request.app
            plugins_dir = plugins_dir_path  # 使用修正后的路径
            logger.info(f"正在扫描插件目录: {plugins_dir}")
            
            # 初始化 plugin_dirs
            plugin_dirs = []
            
            # 检查插件目录是否存在
            if not plugins_dir.exists():
                logger.error(f"插件目录不存在: {plugins_dir}")
            else:
                for plugin_path in plugins_dir.iterdir():
                    if plugin_path.is_dir():
                        plugin_dirs.append(plugin_path)
                        logger.info(f"发现插件目录: {plugin_path.name}")
                
                logger.info(f"总共发现 {len(plugin_dirs)} 个插件目录")
                
                for plugin_path in plugin_dirs:
                    try:
                        await plugin_loader._load_plugin(plugin_path, app)
                        logger.info(f"成功加载插件: {plugin_path.name}")
                    except Exception as e:
                        logger.error(f"加载插件 {plugin_path.name} 失败: {str(e)}")
            
            local_plugins = plugin_loader.list_plugins()
            logger.info(f"plugin_loader.list_plugins() 返回 {len(local_plugins)} 个插件")
            
            # 如果 plugin_loader 返回空，尝试直接读取插件目录中的 JSON 文件
            if not local_plugins:
                logger.info("plugin_loader.list_plugins() 返回空，尝试直接读取插件JSON文件")
                for plugin_path in plugin_dirs:
                    plugin_json_path = plugin_path / "plugin.json"
                    if plugin_json_path.exists():
                        try:
                            with open(plugin_json_path, 'r', encoding='utf-8') as f:
                                plugin = json.load(f)
                                local_plugins.append(plugin)
                                logger.info(f"直接从 {plugin_json_path} 加载插件: {plugin.get('name', '未知')}")
                        except Exception as e:
                            logger.error(f"读取插件JSON文件失败 {plugin_json_path}: {str(e)}")
            
            # Convert local plugins to match store plugin format
            for plugin in local_plugins:
                logger.info(f"处理本地插件: {plugin.get('name', '未知')}")
                # Check if plugin already exists in database by uuid
                existing_plugin = None
                if "uuid" in plugin:
                    existing_plugin = db.query(SysPluginModel).filter(SysPluginModel.uuid == plugin["uuid"]).first()
                    if existing_plugin:
                        logger.info(f"插件 {plugin['uuid']} 在数据库中存在")
                    else:
                        logger.info(f"插件 {plugin['uuid']} 在数据库中不存在")
                
                # Create plugin item
                plugin_item = {
                    "id": existing_plugin.id if existing_plugin else 0,
                    "title": plugin.get("title", plugin.get("name", "")),
                    "author": plugin.get("author", ""),
                    "uuid": plugin.get("uuid", ""),
                    "description": plugin.get("description", ""),
                    "version": plugin.get("version", ""),
                    "downloads": plugin.get("downloads", 0),
                    "download_url": plugin.get("download_url", ""),
                    "md5_hash": plugin.get("md5_hash", ""),
                    "price": float(plugin.get("price", 0.0)),
                    "paid": plugin.get("paid", 0),
                    "installed": plugin.get("installed", 1 if existing_plugin else 0),  # 使用JSON中的installed值
                    "enabled": plugin.get("enabled", 0),
                    "setting_menu": plugin.get("setting_menu", ""),
                    "status": plugin.get("status", "normal"),
                    "created_at": existing_plugin.created_at if existing_plugin else None,
                    "updated_at": existing_plugin.updated_at if existing_plugin else None,
                    "is_local": True,  # Mark as local plugin
                }
                local_items.append(plugin_item)
            
            local_total = len(local_plugins)
            logger.info(f"本地插件处理完成，共 {local_total} 个插件")
        except Exception as e:
            logger.error(f"获取本地插件列表失败: {str(e)}", exc_info=True)
            # Continue without local plugins

    # Combine items based on type
    if type == "all":
        # 全部插件：数据库插件 + 本地插件（基于uuid去重）
        # 创建插件映射，本地插件优先覆盖数据库插件
        plugin_map = {}
        
        # 首先添加所有数据库插件
        for item in store_items:
            plugin_dict = item.to_dict()
            plugin_dict["is_local"] = False
            plugin_dict["installed"] = 1  # 数据库中的插件都是已安装的
            if "uuid" in plugin_dict and plugin_dict["uuid"]:
                plugin_map[plugin_dict["uuid"]] = plugin_dict
            else:
                # 如果没有uuid，使用id作为key
                plugin_map[f"store_{plugin_dict['id']}"] = plugin_dict
        
        # 然后添加本地插件，覆盖相同uuid的数据库插件
        for item in local_items:
            uuid = item.get("uuid")
            if uuid and uuid in plugin_map:
                # 如果uuid已存在（数据库插件），用本地插件数据覆盖
                # 保留数据库插件的id，但使用本地插件的installed值
                existing_plugin = plugin_map[uuid]
                # 更新字段，但保留数据库id
                item["id"] = existing_plugin["id"]
                # 使用本地插件的installed值（来自JSON文件）
                item["is_local"] = True
                plugin_map[uuid] = item
                logger.info(f"插件 {uuid} 使用本地数据覆盖数据库数据")
            elif uuid:
                # 如果uuid不存在，添加新的本地插件
                item["is_local"] = True
                plugin_map[uuid] = item
            else:
                # 如果没有uuid，使用临时key
                item["is_local"] = True
                plugin_map[f"local_{id(item)}"] = item
        
        # 转换为列表
        all_items = list(plugin_map.values())
        
        # Apply search filter if provided
        if search:
            search_lower = search.lower()
            all_items = [
                item for item in all_items
                if (item.get("title", "").lower().find(search_lower) >= 0 or
                    item.get("description", "").lower().find(search_lower) >= 0 or
                    item.get("author", "").lower().find(search_lower) >= 0)
            ]
        
        # Apply sorting if orderby provided
        if orderby:
            # Simple sorting implementation
            field, direction = orderby.split("_") if "_" in orderby else (orderby, "asc")
            reverse = direction.lower() == "desc"
            
            def get_sort_key(item):
                value = item.get(field)
                if value is None:
                    return ""
                return str(value).lower()
            
            all_items.sort(key=get_sort_key, reverse=reverse)
        
        # Apply pagination
        total_items = len(all_items)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_items = all_items[start_idx:end_idx]
        
        return success_response(
            {
                "items": paginated_items,
                "total": total_items,
                "page": page,
                "per_page": per_page,
            }
        )
    
    elif type == "store":
        # Return only store plugins with existing pagination
        return success_response(
            {
                "items": [
                    {**item.to_dict(), "is_local": False} for item in store_items
                ],
                "total": store_total,
                "page": page,
                "per_page": per_page,
            }
        )
    
    else:  # type == "local"
        # Apply search filter to local items
        filtered_local_items = local_items
        if search:
            search_lower = search.lower()
            filtered_local_items = [
                item for item in local_items
                if (item.get("title", "").lower().find(search_lower) >= 0 or
                    item.get("description", "").lower().find(search_lower) >= 0 or
                    item.get("author", "").lower().find(search_lower) >= 0)
            ]
        
        # Apply sorting if orderby provided
        if orderby:
            field, direction = orderby.split("_") if "_" in orderby else (orderby, "asc")
            reverse = direction.lower() == "desc"
            
            def get_sort_key(item):
                value = item.get(field)
                if value is None:
                    return ""
                return str(value).lower()
            
            filtered_local_items.sort(key=get_sort_key, reverse=reverse)
        
        # Apply pagination
        total_local = len(filtered_local_items)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_local_items = filtered_local_items[start_idx:end_idx]
        
        return success_response(
            {
                "items": paginated_local_items,
                "total": total_local,
                "page": page,
                "per_page": per_page,
            }
        )
