# app/plugins/plugin_manager.py
from __future__ import annotations
import os
import sys  # 添加此行以导入 sys 模块
import importlib
from typing import List, Optional
from sqlalchemy.orm import Session
from app.modules.admin.sys_plugin.models.sys_plugin import SysPlugin as PluginModel
from app.modules.admin.sys_plugin.crud.sys_plugin import CRUDSysPlugin
from fastapi import APIRouter
from app.utils.log_utils import logger
from app.core.config import settings


class Plugin:
    def __init__(self, uuid: str):
        self.uuid = uuid
        self.module = None
        self.entry_point = None
        
    def _get_entry_point(self):
        """从 plugin.json 获取插件入口点"""
        try:
            plugin_dir = os.path.join(settings.PLUGINS_DIR, self.uuid)
            plugin_json_path = os.path.join(plugin_dir, "plugin.json")
            
            if os.path.exists(plugin_json_path):
                import json
                with open(plugin_json_path, 'r', encoding='utf-8') as f:
                    plugin_config = json.load(f)
                
                # 获取入口点，默认为 plugin.py
                entry_point = plugin_config.get("entry", {}).get("backend", "plugin.py")
                # 移除 .py 扩展名
                if entry_point.endswith('.py'):
                    entry_point = entry_point[:-3]
                return entry_point
        except Exception as e:
            logger.error(f"Failed to read plugin.json for '{self.uuid}': {e}")
        
        # 默认入口点
        return "plugin"

    def load(self, router: APIRouter):
        try:
            # 获取入口点
            if self.entry_point is None:
                self.entry_point = self._get_entry_point()
            
            # 导入插件模块
            module_name = f"plugins.{self.uuid}.{self.entry_point}"
            self.module = importlib.import_module(module_name)
            
            # 检查是否有 register 函数
            if hasattr(self.module, "register"):
                self.module.register(router)
                logger.info(f"Plugin '{self.uuid}' loaded successfully.")
            else:
                # 如果没有 register 函数，尝试直接包含路由
                if hasattr(self.module, "router"):
                    router.include_router(
                        self.module.router,
                        prefix=f"/api/plugins/{self.uuid}",
                        tags=[self.uuid]
                    )
                    logger.info(f"Plugin '{self.uuid}' loaded via router attribute.")
                else:
                    logger.warning(
                        f"Plugin '{self.uuid}' does not have a 'register' method or 'router' attribute."
                    )
        except Exception as e:
            logger.error(f"Failed to load plugin '{self.uuid}': {e}")

    def unload(self, router: APIRouter):
        try:
            if self.module and hasattr(self.module, "unregister"):
                self.module.unregister(router)
                logger.info(f"Plugin '{self.uuid}' unloaded successfully.")
            # 从 sys.modules 中移除插件模块
            if self.entry_point:
                module_name = f"plugins.{self.uuid}.{self.entry_point}"
            else:
                module_name = f"plugins.{self.uuid}.plugin"
                
            if module_name in sys.modules:
                del sys.modules[module_name]
                logger.info(f"Module '{module_name}' removed from sys.modules.")
        except Exception as e:
            logger.error(f"Failed to unload plugin '{self.uuid}': {e}")


class PluginManager:
    _instance: Optional[PluginManager] = None
    plugins: List[Plugin]  # 类级别声明类型
    db: Session
    plugin_dir: str
    router: Optional[APIRouter]

    def __new__(cls, db: Session):
        if cls._instance is None:
            cls._instance = super(PluginManager, cls).__new__(cls)
            cls._instance.db = db
            cls._instance.plugins = []  # 实例属性赋值，无需类型注解
            cls._instance.plugin_dir = settings.PLUGINS_DIR
            cls._instance.router = None  # 初始化路由为 None
        return cls._instance

    def set_router(self, router: APIRouter):
        self.router = router

    def load_enabled_plugins(self):
        if not self.router:
            raise ValueError("Router not set. Call set_router before loading plugins.")
        
        # 首先从数据库加载已安装且启用的插件
        db_enabled_plugins = (
            self.db.query(PluginModel)
            .filter(PluginModel.installed == 1, PluginModel.enabled == 1)
            .all()
        )
        for plugin_record in db_enabled_plugins:
            self.load_plugin(plugin_record.uuid)
        
        # 然后检查本地插件目录，加载符合条件（installed==1且enabled==1）的插件
        self._load_local_enabled_plugins()
    
    def _load_local_enabled_plugins(self):
        """加载本地插件目录中符合条件的插件（installed==1且enabled==1）"""
        import json
        from pathlib import Path
        
        plugins_dir = Path(self.plugin_dir)
        if not plugins_dir.exists():
            logger.warning(f"插件目录不存在: {plugins_dir}")
            return
        
        for plugin_path in plugins_dir.iterdir():
            if plugin_path.is_dir():
                plugin_json_path = plugin_path / "plugin.json"
                if plugin_json_path.exists():
                    try:
                        with open(plugin_json_path, 'r', encoding='utf-8') as f:
                            plugin_config = json.load(f)
                        
                        # 检查插件是否已安装且启用
                        installed = plugin_config.get("installed", 0)
                        enabled = plugin_config.get("enabled", 0)
                        plugin_uuid = plugin_config.get("uuid", "")
                        
                        if installed == 1 and enabled == 1 and plugin_uuid:
                            # 检查插件是否已经加载
                            if not any(p.uuid == plugin_uuid for p in self.plugins):
                                self.load_plugin(plugin_uuid)
                                logger.info(f"从本地插件目录加载插件: {plugin_uuid} (installed={installed}, enabled={enabled})")
                            else:
                                logger.info(f"插件 {plugin_uuid} 已加载，跳过")
                    except Exception as e:
                        logger.error(f"读取插件配置文件失败 {plugin_json_path}: {str(e)}")

    def load_plugin(self, plugin_uuid: str):
        if any(p.uuid == plugin_uuid for p in self.plugins):
            logger.info(f"Plugin '{plugin_uuid}' is already loaded.")
            return
        plugin = Plugin(uuid=plugin_uuid)
        if self.router:
            plugin.load(self.router)
            self.plugins.append(plugin)
            logger.info(f"Plugin '{plugin_uuid}' loaded and added to plugins list.")
        else:
            logger.warning(f"Cannot load plugin '{plugin_uuid}': router is not set.")

    def unload_plugin(self, plugin_uuid: str):
        plugin = next((p for p in self.plugins if p.uuid == plugin_uuid), None)
        if not plugin:
            logger.info(f"Plugin '{plugin_uuid}' is not loaded.")
            return
        if self.router:
            plugin.unload(self.router)
            self.plugins.remove(plugin)
            logger.info(f"Plugin '{plugin_uuid}' unloaded and removed from plugins list.")
        else:
            logger.warning(f"Cannot unload plugin '{plugin_uuid}': router is not set.")

    def enable_plugin(self, plugin_uuid: str):
        crud_plugin = CRUDSysPlugin()
        plugin_record = crud_plugin.get_by_uuid(db=self.db, uuid=plugin_uuid)
        if not plugin_record:
            raise ValueError(f"Plugin '{plugin_uuid}' not found.")
        
        # 检查插件是否已安装
        if plugin_record.installed != 1:
            raise ValueError(f"Plugin '{plugin_uuid}' is not installed. Cannot enable.")
            
        if plugin_record.enabled == 1:
            logger.info(f"Plugin '{plugin_uuid}' is already enabled.")
            return
        plugin_record.enabled = 1
        self.db.commit()
        self.load_plugin(plugin_uuid)

    def disable_plugin(self, plugin_uuid: str):
        crud_plugin = CRUDSysPlugin()
        plugin_record = crud_plugin.get_by_uuid(db=self.db, uuid=plugin_uuid)
        if not plugin_record:
            raise ValueError(f"Plugin '{plugin_uuid}' not found.")
        
        # 检查插件是否已安装
        if plugin_record.installed != 1:
            raise ValueError(f"Plugin '{plugin_uuid}' is not installed. Cannot disable.")
            
        if plugin_record.enabled == 0:
            logger.info(f"Plugin '{plugin_uuid}' is already disabled.")
            return
        plugin_record.enabled = 0
        self.db.commit()
        self.unload_plugin(plugin_uuid)
