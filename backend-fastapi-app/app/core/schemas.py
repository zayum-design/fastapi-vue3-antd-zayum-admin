# app/core/schemas.py
import importlib
import os
from pathlib import Path

from app.core.config import settings

# 缓存已导入的 schemas 类
_schema_cache = {}


def _import_schema_class(name):
    """动态导入 schemas 类"""
    if name in _schema_cache:
        return _schema_cache[name]

    # 查找 schemas 类 - 支持 admin, common, user 目录
    modules_dir = Path(__file__).parent.parent / "modules"

    # 搜索所有服务目录
    for modules_type in ["admin", "common", "user"]:
        schemas_dir = modules_dir / modules_type

        if not schemas_dir.exists():
            continue

        for schema_file in schemas_dir.glob("**/schemas/*.py"):
            if schema_file.name == "__init__.py":
                continue

            # 构建模块路径
            rel_path = schema_file.relative_to(Path(__file__).parent.parent)
            module_path = str(rel_path).replace("/", ".").replace(".py", "")

            try:
                module = importlib.import_module(f"app.{module_path}")
                if hasattr(module, name):
                    _schema_cache[name] = getattr(module, name)
                    return _schema_cache[name]
            except Exception:
                continue

    raise AttributeError(f"Module 'app.core.schemas' has no attribute '{name}'")


def __getattr__(name):
    """动态获取 schemas 类"""
    return _import_schema_class(name)


def __dir__():
    """返回所有可用的 schemas 类名"""
    modules_dir = Path(__file__).parent.parent / "modules"
    class_names = []

    # 搜索所有服务目录
    for modules_type in ["admin", "common", "user"]:
        schemas_dir = modules_dir / modules_type

        if not schemas_dir.exists():
            continue

        for schema_file in schemas_dir.glob("**/schemas/*.py"):
            if schema_file.name == "__init__.py":
                continue

            # 构建模块路径
            rel_path = schema_file.relative_to(Path(__file__).parent.parent)
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
        if os.path.isdir(plugin_path) and os.path.exists(
            os.path.join(plugin_path, "schemas", "__init__.py")
        ):
            try:
                importlib.import_module(f"plugins.{plugin_name}.schemas")
                print(f"Loaded schemas from plugin: {plugin_name}")
            except Exception as e:
                print(f"Failed to load schemas from plugin {plugin_name}: {e}")
else:
    print(f"Plugin directory not found: {PLUGIN_DIR}")
