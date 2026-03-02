# app/core/models.py
import importlib
import os
from pathlib import Path

from sqlalchemy.orm import declarative_base

# 定义 Base - 必须先定义，避免循环导入
Base = declarative_base()

from app.core.config import settings

# 缓存已导入的模型类和模块
_model_cache = {}
_modules_loaded = False


def _discover_model_modules():
    """发现并返回所有模型模块路径（扫描 app/modules 下所有模块）"""
    modules_dir = Path(__file__).parent.parent / "modules"
    model_modules = []

    # 遍历所有模块（admin, common, user 等）
    for module_dir in modules_dir.iterdir():
        if not module_dir.is_dir() or module_dir.name.startswith("."):
            continue

        # 在每个模块下查找 models/*.py
        for model_file in module_dir.glob("**/models/*.py"):
            if model_file.name == "__init__.py":
                continue

            # 构建模块路径
            rel_path = model_file.relative_to(Path(__file__).parent.parent)
            module_path = str(rel_path).replace("/", ".").replace("\\", ".").replace(".py", "")
            model_modules.append((model_file.name.replace(".py", ""), f"app.{module_path}"))

    return model_modules


def _import_model_class(name):
    """动态导入模型类"""
    if name in _model_cache:
        return _model_cache[name]

    # 查找模型类
    for model_name, module_path in _discover_model_modules():
        try:
            module = importlib.import_module(module_path)
            if hasattr(module, name):
                _model_cache[name] = getattr(module, name)
                return _model_cache[name]
        except Exception:
            continue

    raise AttributeError(f"Module 'app.core.models' has no attribute '{name}'")


def _load_all_models():
    """加载所有模型模块（确保 SQLAlchemy 能收集到所有表）"""
    global _modules_loaded
    if _modules_loaded:
        return

    for model_name, module_path in _discover_model_modules():
        try:
            importlib.import_module(module_path)
        except Exception as e:
            print(f"Failed to load model module {module_path}: {e}")

    _modules_loaded = True


def __getattr__(name):
    """动态获取模型类"""
    return _import_model_class(name)


def __dir__():
    """返回所有可用的模型类名"""
    class_names = []

    for model_name, module_path in _discover_model_modules():
        try:
            module = importlib.import_module(module_path)
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and not attr_name.startswith("_"):
                    class_names.append(attr_name)
        except Exception:
            continue

    return sorted(set(class_names))


# 加载所有模型模块（用于 Alembic 等需要 Base.metadata 的场景）
_load_all_models()


# 插件系统
PLUGIN_DIR = settings.PLUGINS_DIR

if os.path.exists(PLUGIN_DIR):
    for plugin_name in os.listdir(PLUGIN_DIR):
        plugin_path = os.path.join(PLUGIN_DIR, plugin_name)
        if os.path.isdir(plugin_path) and os.path.exists(
            os.path.join(plugin_path, "models", "__init__.py")
        ):
            try:
                importlib.import_module(f"plugins.{plugin_name}.models")
                print(f"Loaded models from plugin: {plugin_name}")
            except Exception as e:
                print(f"Failed to load models from plugin {plugin_name}: {e}")
else:
    print(f"Plugin directory not found: {PLUGIN_DIR}")
