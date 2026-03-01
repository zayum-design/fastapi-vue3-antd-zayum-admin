# app/core/crud.py
import os
import importlib

from app.core.config import settings

# 插件系统
PLUGIN_DIR = settings.PLUGINS_DIR

if os.path.exists(PLUGIN_DIR):
    for plugin_name in os.listdir(PLUGIN_DIR):
        plugin_path = os.path.join(PLUGIN_DIR, plugin_name)
        if os.path.isdir(plugin_path) and os.path.exists(os.path.join(plugin_path, "crud", "__init__.py")):
            try:
                importlib.import_module(f"plugins.{plugin_name}.crud")
                print(f"Loaded crud from plugin: {plugin_name}")
            except Exception as e:
                print(f"Failed to load crud from plugin {plugin_name}: {e}")
else:
    print(f"Plugin directory not found: {PLUGIN_DIR}")
