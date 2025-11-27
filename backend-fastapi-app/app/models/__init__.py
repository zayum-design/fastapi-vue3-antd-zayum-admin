
# server-app/app/models/__init__.py
import os
import importlib

from sqlalchemy.orm import declarative_base

# 定义 Base
Base = declarative_base()

# 显式导入所有模型类
from .sys_admin import SysAdmin
from .sys_admin_group import SysAdminGroup
from .sys_admin_log import SysAdminLog
from .sys_admin_rule import SysAdminRule
from .sys_analytics_summary import SysAnalyticsSummary
from .sys_attachment import SysAttachment
from .sys_attachment_category import SysAttachmentCategory
from .sys_general_category import SysGeneralCategory
from .sys_general_config import SysGeneralConfig
from .sys_notification import SysNotification
from .sys_plugin import SysPlugin
from .sys_user import SysUser
from .sys_user_balance_log import SysUserBalanceLog
from .sys_user_group import SysUserGroup
from .sys_user_rule import SysUserRule
from .sys_user_score_log import SysUserScoreLog
 
PLUGIN_DIR = os.path.join(os.path.dirname(__file__), "../plugins")

for plugin_name in os.listdir(PLUGIN_DIR):
    plugin_path = os.path.join(PLUGIN_DIR, plugin_name)
    if os.path.isdir(plugin_path) and os.path.exists(os.path.join(plugin_path, "models", "__init__.py")):
        try:
            importlib.import_module(f"app.plugins.{plugin_name}.models")
            print(f"Loaded models from plugin: {plugin_name}")
        except Exception as e:
            print(f"Failed to load models from plugin {plugin_name}: {e}")
