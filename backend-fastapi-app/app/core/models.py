# app/core/models.py
import os
import importlib
import sys
from pathlib import Path

from sqlalchemy.orm import declarative_base
from app.core.config import settings

# 定义 Base
Base = declarative_base()

# 缓存已导入的模型类
_model_cache = {}

def _import_model_class(name):
    """动态导入模型类"""
    if name in _model_cache:
        return _model_cache[name]
    
    # 查找模型类
    models_dir = Path(__file__).parent / "modules" / "admin"
    
    for model_file in models_dir.glob("**/models/*.py"):
        if model_file.name == "__init__.py":
            continue
            
        # 构建模块路径
        rel_path = model_file.relative_to(Path(__file__).parent.parent)
        module_path = str(rel_path).replace("/", ".").replace(".py", "")
        
        try:
            module = importlib.import_module(f"app.{module_path}")
            if hasattr(module, name):
                _model_cache[name] = getattr(module, name)
                return _model_cache[name]
        except Exception:
            continue
    
    raise AttributeError(f"Module 'app.core.models' has no attribute '{name}'")

def __getattr__(name):
    """动态获取模型类"""
    return _import_model_class(name)

def __dir__():
    """返回所有可用的模型类名"""
    models_dir = Path(__file__).parent / "modules" / "admin"
    class_names = []
    
    for model_file in models_dir.glob("**/models/*.py"):
        if model_file.name == "__init__.py":
            continue
            
        # 构建模块路径
        rel_path = model_file.relative_to(Path(__file__).parent.parent)
        module_path = str(rel_path).replace("/", ".").replace(".py", "")
        
        try:
            module = importlib.import_module(f"app.{module_path}")
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and not attr_name.startswith("_"):
                    class_names.append(attr_name)
        except Exception:
            continue
    
    return sorted(set(class_names))

# 插件系统
PLUGIN_DIR = settings.PLUGINS_DIR

if os.path.exists(PLUGIN_DIR):
    for plugin_name in os.listdir(PLUGIN_DIR):
        plugin_path = os.path.join(PLUGIN_DIR, plugin_name)
        if os.path.isdir(plugin_path) and os.path.exists(os.path.join(plugin_path, "models", "__init__.py")):
            try:
                importlib.import_module(f"plugins.{plugin_name}.models")
                print(f"Loaded models from plugin: {plugin_name}")
            except Exception as e:
                print(f"Failed to load models from plugin {plugin_name}: {e}")
else:
    print(f"Plugin directory not found: {PLUGIN_DIR}")