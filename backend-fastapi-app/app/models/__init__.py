
# server-app/app/models/__init__.py
import os
import importlib

from sqlalchemy.orm import declarative_base

# 定义 Base
Base = declarative_base()
 
PLUGIN_DIR = os.path.join(os.path.dirname(__file__), "../plugins")

for plugin_name in os.listdir(PLUGIN_DIR):
    plugin_path = os.path.join(PLUGIN_DIR, plugin_name)
    if os.path.isdir(plugin_path) and os.path.exists(os.path.join(plugin_path, "models", "__init__.py")):
        try:
            importlib.import_module(f"app.plugins.{plugin_name}.models")
            print(f"Loaded models from plugin: {plugin_name}")
        except Exception as e:
            print(f"Failed to load models from plugin {plugin_name}: {e}")
