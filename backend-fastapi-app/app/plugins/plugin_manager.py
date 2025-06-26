# app/plugins/plugin_manager.py
from __future__ import annotations
import os
import sys  # 添加此行以导入 sys 模块
import importlib
from typing import List
from sqlalchemy.orm import Session
from app.models.sys_plugin import SysPlugin as PluginModel
from app.crud.sys_plugin import CRUDSysPlugin
from fastapi import APIRouter
from app.utils.log_utils import logger


class Plugin:
    def __init__(self, uuid: str):
        self.uuid = uuid
        self.module = None

    def load(self, router: APIRouter):
        try:
            self.module = importlib.import_module(f"app.plugins.{self.uuid}.plugin")
            if hasattr(self.module, "register"):
                self.module.register(router)
                logger.info(f"Plugin '{self.uuid}' loaded successfully.")
            else:
                logger.warning(
                    f"Plugin '{self.uuid}' does not have a 'register' method."
                )
        except Exception as e:
            logger.error(f"Failed to load plugin '{self.uuid}': {e}")

    def unload(self, router: APIRouter):
        try:
            if hasattr(self.module, "unregister"):
                self.module.unregister(router)
                logger.info(f"Plugin '{self.uuid}' unloaded successfully.")
            # 从 sys.modules 中移除插件模块
            module_name = f"app.plugins.{self.uuid}.plugin"
            if module_name in sys.modules:
                del sys.modules[module_name]
                logger.info(f"Module '{module_name}' removed from sys.modules.")
        except Exception as e:
            logger.error(f"Failed to unload plugin '{self.uuid}': {e}")


class PluginManager:
    _instance: PluginManager = None
    plugins: List[Plugin]  # 类级别声明类型

    def __new__(cls, db: Session):
        if cls._instance is None:
            cls._instance = super(PluginManager, cls).__new__(cls)
            cls._instance.db = db
            cls._instance.plugins = []  # 实例属性赋值，无需类型注解
            cls._instance.plugin_dir = os.path.join(os.path.dirname(__file__), ".")
            cls._instance.router = None  # 初始化路由为 None
        return cls._instance

    def set_router(self, router: APIRouter):
        self.router = router

    def load_enabled_plugins(self):
        if not self.router:
            raise ValueError("Router not set. Call set_router before loading plugins.")
        enabled_plugins = (
            self.db.query(PluginModel).filter(PluginModel.enabled == True).all()
        )
        for plugin_record in enabled_plugins:
            self.load_plugin(plugin_record.uuid)

    def load_plugin(self, plugin_uuid: str):
        if any(p.uuid == plugin_uuid for p in self.plugins):
            logger.info(f"Plugin '{plugin_uuid}' is already loaded.")
            return
        plugin = Plugin(uuid=plugin_uuid)
        plugin.load(self.router)
        self.plugins.append(plugin)
        logger.info(f"Plugin '{plugin_uuid}' loaded and added to plugins list.")

    def unload_plugin(self, plugin_uuid: str):
        plugin = next((p for p in self.plugins if p.uuid == plugin_uuid), None)
        if not plugin:
            logger.info(f"Plugin '{plugin_uuid}' is not loaded.")
            return
        plugin.unload(self.router)
        self.plugins.remove(plugin)
        logger.info(f"Plugin '{plugin_uuid}' unloaded and removed from plugins list.")

    def enable_plugin(self, plugin_uuid: str):
        plugin_record = CRUDSysPlugin.get_by_uuid(db=self.db, uuid=plugin_uuid)
        if not plugin_record:
            raise ValueError(f"Plugin '{plugin_uuid}' not found.")
        if plugin_record.enabled:
            logger.info(f"Plugin '{plugin_uuid}' is already enabled.")
            return
        plugin_record.enabled = True
        self.db.commit()
        self.load_plugin(plugin_uuid)

    def disable_plugin(self, plugin_uuid: str):
        plugin_record = CRUDSysPlugin.get_by_uuid(db=self.db, uuid=plugin_uuid)
        if not plugin_record:
            raise ValueError(f"Plugin '{plugin_uuid}' not found.")
        if not plugin_record.enabled:
            logger.info(f"Plugin '{plugin_uuid}' is already disabled.")
            return
        plugin_record.enabled = False
        self.db.commit()
        self.unload_plugin(plugin_uuid)
