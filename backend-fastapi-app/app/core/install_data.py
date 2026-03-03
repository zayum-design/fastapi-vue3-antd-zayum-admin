"""按模型逐步导入数据（含表结构检查），每个模型一个函数"""
# flake8: noqa: F821  # 模型类通过 _load_models() 动态加载
import importlib
from pathlib import Path
from datetime import datetime
from decimal import Decimal
from sqlalchemy import inspect, create_engine, select
from sqlalchemy.orm import Session
from app.core.db_session import SessionLocal
from app.core.config import settings


def _load_models():
    """动态加载所有模型类到全局命名空间（扫描 app/modules 下所有模块）"""
    modules_dir = Path(__file__).parent.parent.parent / "app" / "modules"
    
    # 遍历所有模块（admin, common, user 等）
    for module_dir in modules_dir.iterdir():
        if not module_dir.is_dir() or module_dir.name.startswith("."):
            continue
        
        for model_file in module_dir.glob("**/models/*.py"):
            if model_file.name == "__init__.py":
                continue
            rel_path = model_file.relative_to(Path(__file__).parent.parent.parent / "app")
            module_path = str(rel_path).replace("/", ".").replace("\\", ".").replace(".py", "")
            try:
                module = importlib.import_module(f"app.{module_path}")
                for attr_name in dir(module):
                    if attr_name.startswith("_"):
                        continue
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type):
                        globals()[attr_name] = attr
            except Exception:
                continue


# 动态加载所有模型
_load_models()

engine = create_engine(settings.DATABASE_URL)
inspector = inspect(engine)

def table_has_data(db: Session, model) -> bool:
    """检查表中是否有数据"""
    return db.scalar(select(model).limit(1)) is not None

def import_SysAdmin(db: Session):
    """导入 SysAdmin 数据"""
    if 'sys_admin' not in inspector.get_table_names():
        print('🔧 创建表: sys_admin')
        SysAdmin.__table__.create(bind=engine)
    else:
        print('✅ 表已存在: sys_admin')
    if not table_has_data(db, SysAdmin):
      print('📥 导入数据: SysAdmin')
      sysadmin_item = SysAdmin()  # noqa: F821
      sysadmin_item.id = 1
      sysadmin_item.group_id = 1
      sysadmin_item.username = 'admin'
      sysadmin_item.nickname = 'SupperAdmin'
      sysadmin_item.password = '$2b$12$PSRSTAdY7Vi8bFgeD5BOA.ZDozJ9rPYVklWGC6y6o7om6QWgR.WlW'
      sysadmin_item.avatar = '/uploads/avatar/avatar_1_c7b7e5.png'
      sysadmin_item.email = '13800000000@qq.com'
      sysadmin_item.mobile = '13800000000'
      sysadmin_item.login_failure = 0
      sysadmin_item.login_at = datetime.fromisoformat('2025-11-29T01:53:50')
      sysadmin_item.login_ip = '127.0.0.1'
      sysadmin_item.token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzY0OTg2MDMwfQ.RE7NJAattKcfoRKYRMUIByfllR85Dj7iXYV5j76L49U'
      sysadmin_item.status = 'normal'
      sysadmin_item.created_at = datetime.fromisoformat('2025-06-26T02:59:10')
      sysadmin_item.updated_at = datetime.fromisoformat('2025-11-29T01:53:50')
      db.add(sysadmin_item)

def import_SysUserBalanceLog(db: Session):
    """导入 SysUserBalanceLog 数据"""
    if 'sys_user_balance_log' not in inspector.get_table_names():
        print('🔧 创建表: sys_user_balance_log')
        SysUserBalanceLog.__table__.create(bind=engine)
    else:
        print('✅ 表已存在: sys_user_balance_log')
    print('ℹ️  表 sys_user_balance_log 无初始数据，无需导入')

def import_SysAttachment(db: Session):
    """导入 SysAttachment 数据"""
    if 'sys_attachment' not in inspector.get_table_names():
        print('🔧 创建表: sys_attachment')
        SysAttachment.__table__.create(bind=engine)
    else:
        print('✅ 表已存在: sys_attachment')
    print('ℹ️  表 sys_attachment 无初始数据，无需导入')

def import_SysGeneralCategory(db: Session):
    """导入 SysGeneralCategory 数据"""
    if 'sys_general_category' not in inspector.get_table_names():
        print('🔧 创建表: sys_general_category')
        SysGeneralCategory.__table__.create(bind=engine)
    else:
        print('✅ 表已存在: sys_general_category')
    if not table_has_data(db, SysGeneralCategory):
      print('📥 导入数据: SysGeneralCategory')
      sysgeneralcategory_item = SysGeneralCategory()  # noqa: F821
      sysgeneralcategory_item.id = 1
      sysgeneralcategory_item.pid = 0
      sysgeneralcategory_item.type = 'default'
      sysgeneralcategory_item.name = 'default'
      sysgeneralcategory_item.thumb = ''
      sysgeneralcategory_item.keywords = ''
      sysgeneralcategory_item.description = ''
      sysgeneralcategory_item.weigh = 0
      sysgeneralcategory_item.status = 'normal'
      sysgeneralcategory_item.created_at = datetime.fromisoformat('2024-05-08T17:19:06')
      sysgeneralcategory_item.updated_at = datetime.fromisoformat('2025-03-07T11:50:19')
      db.add(sysgeneralcategory_item)
      sysgeneralcategory_item = SysGeneralCategory()  # noqa: F821
      sysgeneralcategory_item.id = 2
      sysgeneralcategory_item.pid = 0
      sysgeneralcategory_item.type = 'blog'
      sysgeneralcategory_item.name = 'news'
      sysgeneralcategory_item.thumb = ''
      sysgeneralcategory_item.keywords = ''
      sysgeneralcategory_item.description = ''
      sysgeneralcategory_item.weigh = 0
      sysgeneralcategory_item.status = 'normal'
      sysgeneralcategory_item.created_at = datetime.fromisoformat('2025-06-04T17:47:14')
      sysgeneralcategory_item.updated_at = datetime.fromisoformat('2025-06-04T17:47:14')
      db.add(sysgeneralcategory_item)

def import_SysAdminRule(db: Session):
    """导入 SysAdminRule 数据"""
    if 'sys_admin_rule' not in inspector.get_table_names():
        print('🔧 创建表: sys_admin_rule')
        SysAdminRule.__table__.create(bind=engine)
    else:
        print('✅ 表已存在: sys_admin_rule')
    if not table_has_data(db, SysAdminRule):
      print('📥 导入数据: SysAdminRule')
      sysadminrule_item = SysAdminRule()  # noqa: F821
      sysadminrule_item.id = 1
      sysadminrule_item.rule_type = 'menu'
      sysadminrule_item.parent_id = 0
      sysadminrule_item.name = 'dashboard'
      sysadminrule_item.path = '/dashboard/'
      sysadminrule_item.component = '/_core/dashboard/dashboard'
      sysadminrule_item.redirect = '/dashboard'
      sysadminrule_item.meta = {'icon': 'mdi:view-dashboard-outline', 'title': 'dashboard.dashboard'}
      sysadminrule_item.permission = {}
      sysadminrule_item.menu_display_type = 'addtabs'
      sysadminrule_item.model_name = 'Dashboard'
      sysadminrule_item.deleted_at = datetime.fromisoformat('1970-01-01T00:00:00')
      sysadminrule_item.weigh = 1
      sysadminrule_item.status = 'normal'
      sysadminrule_item.created_at = datetime.fromisoformat('2024-01-22T14:32:00')
      sysadminrule_item.updated_at = datetime.fromisoformat('2025-11-11T01:23:42')
      db.add(sysadminrule_item)
      sysadminrule_item = SysAdminRule()  # noqa: F821
      sysadminrule_item.id = 2
      sysadminrule_item.rule_type = 'menu'
      sysadminrule_item.parent_id = 1
      sysadminrule_item.name = 'workspace'
      sysadminrule_item.path = '/dashboard/workspace'
      sysadminrule_item.component = '/_core/dashboard/workspace/index'
      sysadminrule_item.redirect = ''
      sysadminrule_item.meta = {'icon': 'mdi:view-dashboard-outline', 'title': 'dashboard.workspace.workspace'}
      sysadminrule_item.permission = {'view': True}
      sysadminrule_item.menu_display_type = 'addtabs'
      sysadminrule_item.model_name = 'Dashboard'
      sysadminrule_item.deleted_at = datetime.fromisoformat('1970-01-01T00:00:00')
      sysadminrule_item.weigh = 1
      sysadminrule_item.status = 'normal'
      sysadminrule_item.created_at = datetime.fromisoformat('2024-01-22T14:32:00')
      sysadminrule_item.updated_at = datetime.fromisoformat('2025-06-05T00:22:17')
      db.add(sysadminrule_item)
      sysadminrule_item = SysAdminRule()  # noqa: F821
      sysadminrule_item.id = 3
      sysadminrule_item.rule_type = 'menu'
      sysadminrule_item.parent_id = 0
      sysadminrule_item.name = 'generals'
      sysadminrule_item.path = '/generals'
      sysadminrule_item.component = ''
      sysadminrule_item.redirect = ''
      sysadminrule_item.meta = {'icon': 'mdi:cog-outline', 'title': 'general.general'}
      sysadminrule_item.permission = {}
      sysadminrule_item.menu_display_type = 'addtabs'
      sysadminrule_item.model_name = 'Generals'
      sysadminrule_item.deleted_at = datetime.fromisoformat('1970-01-01T00:00:00')
      sysadminrule_item.weigh = 2
      sysadminrule_item.status = 'normal'
      sysadminrule_item.created_at = datetime.fromisoformat('2024-01-22T14:32:00')
      sysadminrule_item.updated_at = datetime.fromisoformat('2025-02-28T18:40:34')
      db.add(sysadminrule_item)
      sysadminrule_item = SysAdminRule()  # noqa: F821
      sysadminrule_item.id = 4
      sysadminrule_item.rule_type = 'menu'
      sysadminrule_item.parent_id = 3
      sysadminrule_item.name = 'general.profile'
      sysadminrule_item.path = '/general/profile'
      sysadminrule_item.component = '/_core/general/profile'
      sysadminrule_item.redirect = ''
      sysadminrule_item.meta = {'icon': 'mdi:account-outline', 'title': 'general.profile.profile'}
      sysadminrule_item.permission = {'edit': True}
      sysadminrule_item.menu_display_type = 'addtabs'
      sysadminrule_item.model_name = 'GeneralProfile'
      sysadminrule_item.deleted_at = datetime.fromisoformat('1970-01-01T00:00:00')
      sysadminrule_item.weigh = 11
      sysadminrule_item.status = 'normal'
      sysadminrule_item.created_at = datetime.fromisoformat('2024-01-22T14:32:00')
      sysadminrule_item.updated_at = datetime.fromisoformat('2025-02-28T12:04:00')
      db.add(sysadminrule_item)
      sysadminrule_item = SysAdminRule()  # noqa: F821
      sysadminrule_item.id = 5
      sysadminrule_item.rule_type = 'menu'
      sysadminrule_item.parent_id = 3
      sysadminrule_item.name = 'general.category'
      sysadminrule_item.path = '/general/category'
      sysadminrule_item.component = '/_core/general/category'
      sysadminrule_item.redirect = ''
      sysadminrule_item.meta = {'icon': 'mdi:category-plus-outline', 'title': 'general.category.category', 'menuVisibleWithForbidden': 'false'}
      sysadminrule_item.permission = {'add': True, 'edit': True, 'view': True, 'delete': True}
      sysadminrule_item.menu_display_type = 'ajax'
      sysadminrule_item.model_name = 'GeneralsCategory'
      sysadminrule_item.deleted_at = datetime.fromisoformat('1970-01-01T00:00:00')
      sysadminrule_item.weigh = 0
      sysadminrule_item.status = 'normal'
      sysadminrule_item.created_at = datetime.fromisoformat('2025-03-04T03:24:40')
      sysadminrule_item.updated_at = datetime.fromisoformat('2025-03-07T11:12:12')
      db.add(sysadminrule_item)
      sysadminrule_item = SysAdminRule()  # noqa: F821
      sysadminrule_item.id = 6
      sysadminrule_item.rule_type = 'menu'
      sysadminrule_item.parent_id = 3
      sysadminrule_item.name = 'general.config'
      sysadminrule_item.path = '/general/config'
      sysadminrule_item.component = '/_core/general/config'
      sysadminrule_item.redirect = ''
      sysadminrule_item.meta = {'icon': 'mdi:cog-outline', 'title': 'general.config.config'}
      sysadminrule_item.permission = {'add': True, 'edit': True, 'delete': True}
      sysadminrule_item.menu_display_type = 'addtabs'
      sysadminrule_item.model_name = 'GeneralConfig'
      sysadminrule_item.deleted_at = datetime.fromisoformat('1970-01-01T00:00:00')
      sysadminrule_item.weigh = 8
      sysadminrule_item.status = 'normal'
      sysadminrule_item.created_at = datetime.fromisoformat('2024-01-22T14:32:00')
      sysadminrule_item.updated_at = datetime.fromisoformat('2025-03-04T07:36:31')
      db.add(sysadminrule_item)
      sysadminrule_item = SysAdminRule()  # noqa: F821
      sysadminrule_item.id = 7
      sysadminrule_item.rule_type = 'menu'
      sysadminrule_item.parent_id = 0
      sysadminrule_item.name = 'attachments'
      sysadminrule_item.path = '/attachments'
      sysadminrule_item.component = ''
      sysadminrule_item.redirect = ''
      sysadminrule_item.meta = {'icon': 'mdi:paperclip', 'title': 'attachment.attachment_manage'}
      sysadminrule_item.permission = {}
      sysadminrule_item.menu_display_type = 'blank'
      sysadminrule_item.model_name = 'Attachment'
      sysadminrule_item.deleted_at = datetime.fromisoformat('1970-01-01T00:00:00')
      sysadminrule_item.weigh = 9
      sysadminrule_item.status = 'normal'
      sysadminrule_item.created_at = datetime.fromisoformat('2024-01-22T14:32:00')
      sysadminrule_item.updated_at = datetime.fromisoformat('2025-03-06T11:39:00')
      db.add(sysadminrule_item)
      sysadminrule_item = SysAdminRule()  # noqa: F821
      sysadminrule_item.id = 8
      sysadminrule_item.rule_type = 'menu'
      sysadminrule_item.parent_id = 7
      sysadminrule_item.name = 'attachment.attachment'
      sysadminrule_item.path = '/attachment/attachment'
      sysadminrule_item.component = '/_core/attachment/attachment'
      sysadminrule_item.redirect = ''
      sysadminrule_item.meta = {'icon': 'mdi:file-outline', 'title': 'attachment.attachment'}
      sysadminrule_item.permission = {'add': True, 'edit': True, 'view': True, 'delete': True}
      sysadminrule_item.menu_display_type = 'addtabs'
      sysadminrule_item.model_name = 'Attachment'
      sysadminrule_item.deleted_at = datetime.fromisoformat('1970-01-01T00:00:00')
      sysadminrule_item.weigh = 10
      sysadminrule_item.status = 'normal'
      sysadminrule_item.created_at = datetime.fromisoformat('2024-01-22T14:32:00')
      sysadminrule_item.updated_at = datetime.fromisoformat('2025-03-06T11:39:00')
      db.add(sysadminrule_item)
      sysadminrule_item = SysAdminRule()  # noqa: F821
      sysadminrule_item.id = 9
      sysadminrule_item.rule_type = 'menu'
      sysadminrule_item.parent_id = 0
      sysadminrule_item.name = 'plugins'
      sysadminrule_item.path = '/plugins'
      sysadminrule_item.component = ''
      sysadminrule_item.redirect = ''
      sysadminrule_item.meta = {'icon': 'mdi:puzzle-outline', 'title': 'plugin.plugin', 'childComponent': '/_core/general/profile'}
      sysadminrule_item.permission = {}
      sysadminrule_item.menu_display_type = 'addtabs'
      sysadminrule_item.model_name = 'Plugin'
      sysadminrule_item.deleted_at = datetime.fromisoformat('1970-01-01T00:00:00')
      sysadminrule_item.weigh = 3
      sysadminrule_item.status = 'normal'
      sysadminrule_item.created_at = datetime.fromisoformat('2024-01-22T14:32:00')
      sysadminrule_item.updated_at = datetime.fromisoformat('2025-02-28T17:51:12')
      db.add(sysadminrule_item)
      sysadminrule_item = SysAdminRule()  # noqa: F821
      sysadminrule_item.id = 10
      sysadminrule_item.rule_type = 'menu'
      sysadminrule_item.parent_id = 0
      sysadminrule_item.name = 'admin'
      sysadminrule_item.path = '/admin'
      sysadminrule_item.component = ''
      sysadminrule_item.redirect = ''
      sysadminrule_item.meta = {'icon': 'mdi:shield-account-outline', 'title': 'admin.admin.field.admin'}
      sysadminrule_item.permission = {}
      sysadminrule_item.menu_display_type = 'addtabs'
      sysadminrule_item.model_name = 'Admin'
      sysadminrule_item.deleted_at = datetime.fromisoformat('1970-01-01T00:00:00')
      sysadminrule_item.weigh = 4
      sysadminrule_item.status = 'normal'
      sysadminrule_item.created_at = datetime.fromisoformat('2024-01-22T14:32:00')
      sysadminrule_item.updated_at = datetime.fromisoformat('2025-06-04T12:15:36')
      db.add(sysadminrule_item)
      sysadminrule_item = SysAdminRule()  # noqa: F821
      sysadminrule_item.id = 11
      sysadminrule_item.rule_type = 'menu'
      sysadminrule_item.parent_id = 10
      sysadminrule_item.name = 'admin.admin'
      sysadminrule_item.path = '/admin/admin'
      sysadminrule_item.component = '/_core/admin/admin'
      sysadminrule_item.redirect = ''
      sysadminrule_item.meta = {'icon': 'mdi:account-outline', 'title': 'admin.admin.admin_manage'}
      sysadminrule_item.permission = {'add': True, 'ajax': True, 'edit': True, 'view': True, 'delete': True}
      sysadminrule_item.menu_display_type = 'addtabs'
      sysadminrule_item.model_name = 'Admin'
      sysadminrule_item.deleted_at = datetime.fromisoformat('1970-01-01T00:00:00')
      sysadminrule_item.weigh = 20
      sysadminrule_item.status = 'normal'
      sysadminrule_item.created_at = datetime.fromisoformat('2024-01-22T14:32:00')
      sysadminrule_item.updated_at = datetime.fromisoformat('2025-03-06T16:24:24')
      db.add(sysadminrule_item)
      sysadminrule_item = SysAdminRule()  # noqa: F821
      sysadminrule_item.id = 12
      sysadminrule_item.rule_type = 'menu'
      sysadminrule_item.parent_id = 10
      sysadminrule_item.name = 'admin.group'
      sysadminrule_item.path = '/admin/group'
      sysadminrule_item.component = '/_core/admin/group'
      sysadminrule_item.redirect = ''
      sysadminrule_item.meta = {'icon': 'mdi:account-group-outline', 'title': 'admin.group.group'}
      sysadminrule_item.permission = {'add': True, 'ajax': True, 'edit': True, 'view': True, 'delete': True}
      sysadminrule_item.menu_display_type = 'addtabs'
      sysadminrule_item.model_name = 'AdminGroup'
      sysadminrule_item.deleted_at = datetime.fromisoformat('1970-01-01T00:00:00')
      sysadminrule_item.weigh = 21
      sysadminrule_item.status = 'normal'
      sysadminrule_item.created_at = datetime.fromisoformat('2024-01-22T14:32:00')
      sysadminrule_item.updated_at = datetime.fromisoformat('2025-03-06T13:03:05')
      db.add(sysadminrule_item)
      sysadminrule_item = SysAdminRule()  # noqa: F821
      sysadminrule_item.id = 13
      sysadminrule_item.rule_type = 'menu'
      sysadminrule_item.parent_id = 10
      sysadminrule_item.name = 'admin.rule'
      sysadminrule_item.path = '/admin/rule'
      sysadminrule_item.component = '/_core/admin/rule'
      sysadminrule_item.redirect = ''
      sysadminrule_item.meta = {'icon': 'mdi:shield-account-outline', 'title': 'admin.rule.rule'}
      sysadminrule_item.permission = {'add': True, 'edit': True, 'view': True, 'delete': True}
      sysadminrule_item.menu_display_type = 'addtabs'
      sysadminrule_item.model_name = 'AdminRule'
      sysadminrule_item.deleted_at = datetime.fromisoformat('1970-01-01T00:00:00')
      sysadminrule_item.weigh = 47
      sysadminrule_item.status = 'normal'
      sysadminrule_item.created_at = datetime.fromisoformat('2024-01-22T14:32:00')
      sysadminrule_item.updated_at = datetime.fromisoformat('2025-03-06T13:03:05')
      db.add(sysadminrule_item)
      sysadminrule_item = SysAdminRule()  # noqa: F821
      sysadminrule_item.id = 14
      sysadminrule_item.rule_type = 'menu'
      sysadminrule_item.parent_id = 10
      sysadminrule_item.name = 'admin.log'
      sysadminrule_item.path = '/admin/log'
      sysadminrule_item.component = '/_core/admin/log'
      sysadminrule_item.redirect = ''
      sysadminrule_item.meta = {'icon': 'mdi:clipboard-text-outline', 'title': 'admin.log.log'}
      sysadminrule_item.permission = {'view': True}
      sysadminrule_item.menu_display_type = 'addtabs'
      sysadminrule_item.model_name = 'AdminLog'
      sysadminrule_item.deleted_at = datetime.fromisoformat('1970-01-01T00:00:00')
      sysadminrule_item.weigh = 50
      sysadminrule_item.status = 'normal'
      sysadminrule_item.created_at = datetime.fromisoformat('2024-01-22T14:32:00')
      sysadminrule_item.updated_at = datetime.fromisoformat('2025-03-04T07:36:31')
      db.add(sysadminrule_item)
      sysadminrule_item = SysAdminRule()  # noqa: F821
      sysadminrule_item.id = 15
      sysadminrule_item.rule_type = 'menu'
      sysadminrule_item.parent_id = 0
      sysadminrule_item.name = 'users'
      sysadminrule_item.path = '/users'
      sysadminrule_item.component = ''
      sysadminrule_item.redirect = ''
      sysadminrule_item.meta = {'icon': 'mdi:account-multiple-outline', 'title': 'user.user'}
      sysadminrule_item.permission = {}
      sysadminrule_item.menu_display_type = 'addtabs'
      sysadminrule_item.model_name = 'Users'
      sysadminrule_item.deleted_at = datetime.fromisoformat('1970-01-01T00:00:00')
      sysadminrule_item.weigh = 24
      sysadminrule_item.status = 'normal'
      sysadminrule_item.created_at = datetime.fromisoformat('2024-01-22T14:32:00')
      sysadminrule_item.updated_at = datetime.fromisoformat('2025-02-26T17:47:48')
      db.add(sysadminrule_item)
      sysadminrule_item = SysAdminRule()  # noqa: F821
      sysadminrule_item.id = 16
      sysadminrule_item.rule_type = 'menu'
      sysadminrule_item.parent_id = 15
      sysadminrule_item.name = 'user'
      sysadminrule_item.path = '/user'
      sysadminrule_item.component = '/_core/user/user'
      sysadminrule_item.redirect = ''
      sysadminrule_item.meta = {'icon': 'mdi:account-outline', 'title': 'user.user_manage'}
      sysadminrule_item.permission = {'add': True, 'edit': True, 'view': True, 'delete': True}
      sysadminrule_item.menu_display_type = 'addtabs'
      sysadminrule_item.model_name = 'User'
      sysadminrule_item.deleted_at = datetime.fromisoformat('1970-01-01T00:00:00')
      sysadminrule_item.weigh = 24
      sysadminrule_item.status = 'normal'
      sysadminrule_item.created_at = datetime.fromisoformat('2024-01-22T14:32:00')
      sysadminrule_item.updated_at = datetime.fromisoformat('2025-03-06T16:19:59')
      db.add(sysadminrule_item)
      sysadminrule_item = SysAdminRule()  # noqa: F821
      sysadminrule_item.id = 17
      sysadminrule_item.rule_type = 'menu'
      sysadminrule_item.parent_id = 15
      sysadminrule_item.name = 'user.rule'
      sysadminrule_item.path = '/user/rule'
      sysadminrule_item.component = '/_core/user/rule'
      sysadminrule_item.redirect = ''
      sysadminrule_item.meta = {'icon': 'mdi:shield-account-outline', 'title': 'user.rule.rule'}
      sysadminrule_item.permission = {'add': True, 'edit': True, 'view': True, 'delete': True}
      sysadminrule_item.menu_display_type = 'addtabs'
      sysadminrule_item.model_name = 'UserRule'
      sysadminrule_item.deleted_at = datetime.fromisoformat('1970-01-01T00:00:00')
      sysadminrule_item.weigh = 26
      sysadminrule_item.status = 'normal'
      sysadminrule_item.created_at = datetime.fromisoformat('2024-01-22T14:32:00')
      sysadminrule_item.updated_at = datetime.fromisoformat('2025-03-04T07:36:31')
      db.add(sysadminrule_item)
      sysadminrule_item = SysAdminRule()  # noqa: F821
      sysadminrule_item.id = 18
      sysadminrule_item.rule_type = 'menu'
      sysadminrule_item.parent_id = 15
      sysadminrule_item.name = 'user.balance.log'
      sysadminrule_item.path = '/user/balance/log'
      sysadminrule_item.component = '/_core/user/balance_log'
      sysadminrule_item.redirect = ''
      sysadminrule_item.meta = {'icon': 'mdi:account-balance-wallet-outline', 'title': 'user.balance_log.balance_log'}
      sysadminrule_item.permission = {'add': True, 'edit': True, 'view': True, 'delete': True}
      sysadminrule_item.menu_display_type = 'addtabs'
      sysadminrule_item.model_name = 'UserBalance'
      sysadminrule_item.deleted_at = datetime.fromisoformat('1970-01-01T00:00:00')
      sysadminrule_item.weigh = 25
      sysadminrule_item.status = 'normal'
      sysadminrule_item.created_at = datetime.fromisoformat('2024-01-22T14:32:00')
      sysadminrule_item.updated_at = datetime.fromisoformat('2025-03-06T16:27:28')
      db.add(sysadminrule_item)
      sysadminrule_item = SysAdminRule()  # noqa: F821
      sysadminrule_item.id = 19
      sysadminrule_item.rule_type = 'menu'
      sysadminrule_item.parent_id = 15
      sysadminrule_item.name = 'user.score.log'
      sysadminrule_item.path = '/user/score/log'
      sysadminrule_item.component = '/_core/user/score_log'
      sysadminrule_item.redirect = ''
      sysadminrule_item.meta = {'icon': 'mdi:scoreboard-outline', 'title': 'user.score_log.score_log'}
      sysadminrule_item.permission = {'add': True, 'edit': True, 'view': True, 'delete': True}
      sysadminrule_item.menu_display_type = 'addtabs'
      sysadminrule_item.model_name = 'UserScore'
      sysadminrule_item.deleted_at = datetime.fromisoformat('1970-01-01T00:00:00')
      sysadminrule_item.weigh = 25
      sysadminrule_item.status = 'normal'
      sysadminrule_item.created_at = datetime.fromisoformat('2024-01-22T14:32:00')
      sysadminrule_item.updated_at = datetime.fromisoformat('2025-03-06T16:28:37')
      db.add(sysadminrule_item)
      sysadminrule_item = SysAdminRule()  # noqa: F821
      sysadminrule_item.id = 20
      sysadminrule_item.rule_type = 'menu'
      sysadminrule_item.parent_id = 15
      sysadminrule_item.name = 'user.group'
      sysadminrule_item.path = '/user/group'
      sysadminrule_item.component = '/_core/user/group'
      sysadminrule_item.redirect = ''
      sysadminrule_item.meta = {'icon': 'mdi:account-group-outline', 'title': 'user.group.group'}
      sysadminrule_item.permission = {'add': True, 'edit': True, 'view': True, 'delete': True}
      sysadminrule_item.menu_display_type = 'addtabs'
      sysadminrule_item.model_name = 'UserGroup'
      sysadminrule_item.deleted_at = datetime.fromisoformat('1970-01-01T00:00:00')
      sysadminrule_item.weigh = 0
      sysadminrule_item.status = 'normal'
      sysadminrule_item.created_at = datetime.fromisoformat('2024-09-26T13:01:14')
      sysadminrule_item.updated_at = datetime.fromisoformat('2025-03-04T07:36:31')
      db.add(sysadminrule_item)
      sysadminrule_item = SysAdminRule()  # noqa: F821
      sysadminrule_item.id = 22
      sysadminrule_item.rule_type = 'menu'
      sysadminrule_item.parent_id = 9
      sysadminrule_item.name = 'generator'
      sysadminrule_item.path = '/plugins/generator'
      sysadminrule_item.component = '/plugins/generator'
      sysadminrule_item.redirect = ''
      sysadminrule_item.meta = {'icon': 'mdi:codepen', 'title': 'generator.code_generator', 'menuVisibleWithForbidden': 'false'}
      sysadminrule_item.permission = {'view': True}
      sysadminrule_item.menu_display_type = 'ajax'
      sysadminrule_item.model_name = 'generator'
      sysadminrule_item.deleted_at = datetime.fromisoformat('1970-01-01T00:00:00')
      sysadminrule_item.weigh = 0
      sysadminrule_item.status = 'normal'
      sysadminrule_item.created_at = datetime.fromisoformat('2025-02-28T10:31:33')
      sysadminrule_item.updated_at = datetime.fromisoformat('2025-03-04T07:36:31')
      db.add(sysadminrule_item)
      sysadminrule_item = SysAdminRule()  # noqa: F821
      sysadminrule_item.id = 24
      sysadminrule_item.rule_type = 'menu'
      sysadminrule_item.parent_id = 7
      sysadminrule_item.name = 'attachmentCategory'
      sysadminrule_item.path = '/attachment/category'
      sysadminrule_item.component = '/_core/attachment/category'
      sysadminrule_item.redirect = ''
      sysadminrule_item.meta = {'icon': 'mdi:attachment', 'title': 'attachment.category.category', 'menuVisibleWithForbidden': 'false'}
      sysadminrule_item.permission = {'add': True, 'edit': True, 'view': True, 'delete': True}
      sysadminrule_item.menu_display_type = 'ajax'
      sysadminrule_item.model_name = 'attachmentCategory'
      sysadminrule_item.deleted_at = datetime.fromisoformat('1970-01-01T00:00:00')
      sysadminrule_item.weigh = 0
      sysadminrule_item.status = 'normal'
      sysadminrule_item.created_at = datetime.fromisoformat('2025-03-06T03:54:07')
      sysadminrule_item.updated_at = datetime.fromisoformat('2025-03-06T12:56:31')
      db.add(sysadminrule_item)
      sysadminrule_item = SysAdminRule()  # noqa: F821
      sysadminrule_item.id = 25
      sysadminrule_item.rule_type = 'menu'
      sysadminrule_item.parent_id = 9
      sysadminrule_item.name = 'plugin'
      sysadminrule_item.path = '/plugin/plugin'
      sysadminrule_item.component = '/_core/plugin/plugin'
      sysadminrule_item.redirect = ''
      sysadminrule_item.meta = {'icon': 'mdi:shape-rectangle-add', 'title': 'plugin.plugin', 'menuVisibleWithForbidden': 'false'}
      sysadminrule_item.permission = {'add': True, 'edit': True, 'view': True, 'delete': True}
      sysadminrule_item.menu_display_type = 'ajax'
      sysadminrule_item.model_name = 'plugin'
      sysadminrule_item.deleted_at = datetime.fromisoformat('1970-01-01T00:00:00')
      sysadminrule_item.weigh = 0
      sysadminrule_item.status = 'normal'
      sysadminrule_item.created_at = datetime.fromisoformat('2025-03-09T02:40:04')
      sysadminrule_item.updated_at = datetime.fromisoformat('2025-03-09T11:05:32')
      db.add(sysadminrule_item)
      sysadminrule_item = SysAdminRule()  # noqa: F821
      sysadminrule_item.id = 26
      sysadminrule_item.rule_type = 'menu'
      sysadminrule_item.parent_id = 9
      sysadminrule_item.name = 'plugin_store'
      sysadminrule_item.path = '/plugin/plugin_store'
      sysadminrule_item.component = '/_core/plugin_store'
      sysadminrule_item.redirect = ''
      sysadminrule_item.meta = {'icon': 'mdi:all-inclusive', 'title': 'plugin.plugin_store', 'menuVisibleWithForbidden': 'false'}
      sysadminrule_item.permission = {'enable': True, 'disable': True, 'install': True, 'unstall': True}
      sysadminrule_item.menu_display_type = 'ajax'
      sysadminrule_item.model_name = 'online_plugin'
      sysadminrule_item.deleted_at = datetime.fromisoformat('1970-01-01T00:00:00')
      sysadminrule_item.weigh = 0
      sysadminrule_item.status = 'normal'
      sysadminrule_item.created_at = datetime.fromisoformat('2025-03-10T07:15:54')
      sysadminrule_item.updated_at = datetime.fromisoformat('2025-03-10T16:07:41')
      db.add(sysadminrule_item)
      sysadminrule_item = SysAdminRule()  # noqa: F821
      sysadminrule_item.id = 27
      sysadminrule_item.rule_type = 'menu'
      sysadminrule_item.parent_id = 1
      sysadminrule_item.name = 'analytics'
      sysadminrule_item.path = '/dashboard/analytics'
      sysadminrule_item.component = '/_core/dashboard/analytics/index'
      sysadminrule_item.redirect = ''
      sysadminrule_item.meta = {'icon': 'mdi:view-dashboard-outline', 'title': 'dashboard.analytics'}
      sysadminrule_item.permission = {'view': True}
      sysadminrule_item.menu_display_type = 'addtabs'
      sysadminrule_item.model_name = 'Dashboard'
      sysadminrule_item.deleted_at = datetime.fromisoformat('1970-01-01T00:00:00')
      sysadminrule_item.weigh = 1
      sysadminrule_item.status = 'normal'
      sysadminrule_item.created_at = datetime.fromisoformat('2024-01-22T14:32:00')
      sysadminrule_item.updated_at = datetime.fromisoformat('2025-03-04T07:36:31')
      db.add(sysadminrule_item)

def import_SysNotification(db: Session):
    """导入 SysNotification 数据"""
    if 'sys_notification' not in inspector.get_table_names():
        print('🔧 创建表: sys_notification')
        SysNotification.__table__.create(bind=engine)
    else:
        print('✅ 表已存在: sys_notification')
    print('ℹ️  表 sys_notification 无初始数据，无需导入')

def import_SysAdminLog(db: Session):
    """导入 SysAdminLog 数据"""
    if 'sys_admin_log' not in inspector.get_table_names():
        print('🔧 创建表: sys_admin_log')
        SysAdminLog.__table__.create(bind=engine)
    else:
        print('✅ 表已存在: sys_admin_log')
    if not table_has_data(db, SysAdminLog):
      print('📥 导入数据: SysAdminLog')
      sysadminlog_item = SysAdminLog()  # noqa: F821
      sysadminlog_item.id = 1
      sysadminlog_item.admin_id = 1
      sysadminlog_item.username = 'admin'
      sysadminlog_item.url = 'http://127.0.0.1:8000/api/admin/user/create'
      sysadminlog_item.title = 'POST'
      sysadminlog_item.content = '{"user_group_id": 1, "username": "uuuu", "nickname": "uuuu", "password": "*", "email": "dsfa@ddd.ccc", "mobile": "13345443233", "avatar": "", "level": 0, "gender": "male", "birthday": "2025-11-27", "bio": "", "balance": 0, "score": 0, "successions": 0, "max_successions": 0, "prev_time": "2025-11-27 11:58:30", "login_time": "2025-11-27 11:58:30", "login_ip": "", "login_failure": 0, "join_ip": "", "verification": "", "token": "", "status": "normal", "platform": "web", "created_at": "2025-11-27 11:58:30", "updated_at": "2025-11-27 11:58:30"}'
      sysadminlog_item.ip = '127.0.0.1'
      sysadminlog_item.useragent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36'
      sysadminlog_item.created_at = datetime.fromisoformat('2025-11-27T03:59:30')
      sysadminlog_item.updated_at = datetime.fromisoformat('2025-11-27T03:59:30')
      db.add(sysadminlog_item)
      sysadminlog_item = SysAdminLog()  # noqa: F821
      sysadminlog_item.id = 2
      sysadminlog_item.admin_id = 1
      sysadminlog_item.username = 'admin'
      sysadminlog_item.url = 'http://127.0.0.1:8000/api/admin/admin/update/1'
      sysadminlog_item.title = 'PUT'
      sysadminlog_item.content = '{"id": 1, "group_id": 1, "username": "admin", "nickname": "SupperAdmin", "avatar": "/uploads/avatar/avatar_1_c7b7e5.png", "email": "13800000000@qq.com", "mobile": "13800000000", "login_failure": 0, "login_at": "2025-11-29 01:26:27", "login_ip": "127.0.0.1", "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzY0OTg0Mzg3fQ.6kogc16gtD9ipLIr7eqrwgBCRQvtSdkBTx5VvFJF6oQ", "status": "normal", "created_at": "2025-06-26 02:59:10", "updated_at": "2025-11-29 01:26:27", "password": "*"}'
      sysadminlog_item.ip = '127.0.0.1'
      sysadminlog_item.useragent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36'
      sysadminlog_item.created_at = datetime.fromisoformat('2025-11-29T01:53:39')
      sysadminlog_item.updated_at = datetime.fromisoformat('2025-11-29T01:53:39')
      db.add(sysadminlog_item)

def import_SysUserRule(db: Session):
    """导入 SysUserRule 数据"""
    if 'sys_user_rule' not in inspector.get_table_names():
        print('🔧 创建表: sys_user_rule')
        SysUserRule.__table__.create(bind=engine)
    else:
        print('✅ 表已存在: sys_user_rule')
    if not table_has_data(db, SysUserRule):
      print('📥 导入数据: SysUserRule')
      sysuserrule_item = SysUserRule()  # noqa: F821
      sysuserrule_item.id = 1
      sysuserrule_item.rule_type = 'menu'
      sysuserrule_item.parent_id = 0
      sysuserrule_item.name = 'userHome'
      sysuserrule_item.path = '/home'
      sysuserrule_item.component = '/user/home'
      sysuserrule_item.redirect = '/dashboard'
      sysuserrule_item.meta = {'icon': 'mdi:home', 'title': 'home.home'}
      sysuserrule_item.permission = {}
      sysuserrule_item.menu_display_type = 'addtabs'
      sysuserrule_item.model_name = 'Home'
      sysuserrule_item.deleted_at = datetime.fromisoformat('1970-01-01T00:00:00')
      sysuserrule_item.weigh = 1
      sysuserrule_item.status = 'normal'
      sysuserrule_item.created_at = datetime.fromisoformat('2024-01-22T14:32:00')
      sysuserrule_item.updated_at = datetime.fromisoformat('2025-07-01T09:21:36')
      db.add(sysuserrule_item)
      sysuserrule_item = SysUserRule()  # noqa: F821
      sysuserrule_item.id = 2
      sysuserrule_item.rule_type = 'menu'
      sysuserrule_item.parent_id = 0
      sysuserrule_item.name = 'userProfile'
      sysuserrule_item.path = '/profile'
      sysuserrule_item.component = '/user/profile'
      sysuserrule_item.redirect = ''
      sysuserrule_item.meta = {'icon': 'mdi:account', 'title': 'profile.profile'}
      sysuserrule_item.permission = {}
      sysuserrule_item.menu_display_type = 'addtabs'
      sysuserrule_item.model_name = 'Profile'
      sysuserrule_item.deleted_at = datetime.fromisoformat('1970-01-01T00:00:00')
      sysuserrule_item.weigh = 1
      sysuserrule_item.status = 'normal'
      sysuserrule_item.created_at = datetime.fromisoformat('2024-01-22T14:32:00')
      sysuserrule_item.updated_at = datetime.fromisoformat('2025-07-01T09:22:00')
      db.add(sysuserrule_item)
      sysuserrule_item = SysUserRule()  # noqa: F821
      sysuserrule_item.id = 3
      sysuserrule_item.rule_type = 'menu'
      sysuserrule_item.parent_id = 0
      sysuserrule_item.name = 'userSetting'
      sysuserrule_item.path = '/setting'
      sysuserrule_item.component = '/user/setting'
      sysuserrule_item.redirect = ''
      sysuserrule_item.meta = {'icon': 'mdi:cog', 'title': 'setting.setting'}
      sysuserrule_item.permission = {}
      sysuserrule_item.menu_display_type = 'addtabs'
      sysuserrule_item.model_name = 'Setting'
      sysuserrule_item.deleted_at = datetime.fromisoformat('1970-01-01T00:00:00')
      sysuserrule_item.weigh = 2
      sysuserrule_item.status = 'normal'
      sysuserrule_item.created_at = datetime.fromisoformat('2024-01-22T14:32:00')
      sysuserrule_item.updated_at = datetime.fromisoformat('2025-07-01T09:21:36')
      db.add(sysuserrule_item)

def import_SysAdminGroup(db: Session):
    """导入 SysAdminGroup 数据"""
    if 'sys_admin_group' not in inspector.get_table_names():
        print('🔧 创建表: sys_admin_group')
        SysAdminGroup.__table__.create(bind=engine)
    else:
        print('✅ 表已存在: sys_admin_group')
    if not table_has_data(db, SysAdminGroup):
      print('📥 导入数据: SysAdminGroup')
      sysadmingroup_item = SysAdminGroup()  # noqa: F821
      sysadmingroup_item.id = 1
      sysadmingroup_item.pid = 0
      sysadmingroup_item.name = 'super'
      sysadmingroup_item.rules = ['all']
      sysadmingroup_item.access = ['all']
      sysadmingroup_item.status = 'normal'
      sysadmingroup_item.created_at = datetime.fromisoformat('2024-04-05T12:15:11')
      sysadmingroup_item.updated_at = datetime.fromisoformat('2025-03-04T15:54:49')
      db.add(sysadmingroup_item)

def import_SysPlugin(db: Session):
    """导入 SysPlugin 数据"""
    if 'sys_plugin' not in inspector.get_table_names():
        print('🔧 创建表: sys_plugin')
        SysPlugin.__table__.create(bind=engine)
    else:
        print('✅ 表已存在: sys_plugin')
    if not table_has_data(db, SysPlugin):
      print('📥 导入数据: SysPlugin')
      sysplugin_item = SysPlugin()  # noqa: F821
      sysplugin_item.id = 1
      sysplugin_item.title = '代码生成器'
      sysplugin_item.author = 'StkFish'
      sysplugin_item.uuid = 'generator'
      sysplugin_item.description = 'generator'
      sysplugin_item.version = '1.0.1'
      sysplugin_item.downloads = 12
      sysplugin_item.download_url = '2'
      sysplugin_item.md5_hash = '2'
      sysplugin_item.price = 10.0
      sysplugin_item.paid = 0
      sysplugin_item.installed = 1
      sysplugin_item.enabled = 1
      sysplugin_item.setting_menu = '0'
      sysplugin_item.status = 'normal'
      sysplugin_item.created_at = datetime.fromisoformat('2025-03-10T17:09:22')
      sysplugin_item.updated_at = datetime.fromisoformat('2025-05-09T09:34:40')
      db.add(sysplugin_item)

def import_SysUser(db: Session):
    """导入 SysUser 数据"""
    if 'sys_user' not in inspector.get_table_names():
        print('🔧 创建表: sys_user')
        SysUser.__table__.create(bind=engine)
    else:
        print('✅ 表已存在: sys_user')
    if not table_has_data(db, SysUser):
      print('📥 导入数据: SysUser')
      sysuser_item = SysUser()  # noqa: F821
      sysuser_item.id = 1
      sysuser_item.user_group_id = 1
      sysuser_item.username = 'uuuu'
      sysuser_item.nickname = 'uuuu'
      sysuser_item.password = '$2b$12$klAmaDRXn/io90Jxjh6/2O0pfwErn9PL7CNWhWBzE2Kq9c6o83O5K'
      sysuser_item.email = 'dsfa@ddd.ccc'
      sysuser_item.mobile = '13345443233'
      sysuser_item.avatar = ''
      sysuser_item.level = 0
      sysuser_item.gender = 'male'
      sysuser_item.birthday = datetime.fromisoformat('2025-11-27')
      sysuser_item.bio = ''
      sysuser_item.balance = Decimal('0.00')
      sysuser_item.score = 0
      sysuser_item.successions = 0
      sysuser_item.max_successions = 0
      sysuser_item.prev_time = datetime.fromisoformat('2025-11-27T11:58:30')
      sysuser_item.login_time = datetime.fromisoformat('2025-11-27T11:58:30')
      sysuser_item.login_ip = ''
      sysuser_item.login_failure = 0
      sysuser_item.join_ip = ''
      sysuser_item.verification = ''
      sysuser_item.token = ''
      sysuser_item.status = 'normal'
      sysuser_item.platform = 'web'
      sysuser_item.created_at = datetime.fromisoformat('2025-11-27T11:58:30')
      sysuser_item.updated_at = datetime.fromisoformat('2025-11-27T11:58:30')
      db.add(sysuser_item)

def import_SysUserScoreLog(db: Session):
    """导入 SysUserScoreLog 数据"""
    if 'sys_user_score_log' not in inspector.get_table_names():
        print('🔧 创建表: sys_user_score_log')
        SysUserScoreLog.__table__.create(bind=engine)
    else:
        print('✅ 表已存在: sys_user_score_log')
    print('ℹ️  表 sys_user_score_log 无初始数据，无需导入')

def import_SysAnalyticsSummary(db: Session):
    """导入 SysAnalyticsSummary 数据"""
    if 'sys_analytics_summary' not in inspector.get_table_names():
        print('🔧 创建表: sys_analytics_summary')
        SysAnalyticsSummary.__table__.create(bind=engine)
    else:
        print('✅ 表已存在: sys_analytics_summary')
    print('ℹ️  表 sys_analytics_summary 无初始数据，无需导入')

def import_SysAttachmentCategory(db: Session):
    """导入 SysAttachmentCategory 数据"""
    if 'sys_attachment_category' not in inspector.get_table_names():
        print('🔧 创建表: sys_attachment_category')
        SysAttachmentCategory.__table__.create(bind=engine)
    else:
        print('✅ 表已存在: sys_attachment_category')
    if not table_has_data(db, SysAttachmentCategory):
      print('📥 导入数据: SysAttachmentCategory')
      sysattachmentcategory_item = SysAttachmentCategory()  # noqa: F821
      sysattachmentcategory_item.id = 1
      sysattachmentcategory_item.pid = 0
      sysattachmentcategory_item.name = 'default'
      sysattachmentcategory_item.status = 'normal'
      sysattachmentcategory_item.created_at = datetime.fromisoformat('2025-03-06T12:00:02')
      sysattachmentcategory_item.updated_at = datetime.fromisoformat('2025-03-07T09:10:48')
      db.add(sysattachmentcategory_item)

def import_SysUserGroup(db: Session):
    """导入 SysUserGroup 数据"""
    if 'sys_user_group' not in inspector.get_table_names():
        print('🔧 创建表: sys_user_group')
        SysUserGroup.__table__.create(bind=engine)
    else:
        print('✅ 表已存在: sys_user_group')
    if not table_has_data(db, SysUserGroup):
      print('📥 导入数据: SysUserGroup')
      sysusergroup_item = SysUserGroup()  # noqa: F821
      sysusergroup_item.id = 1
      sysusergroup_item.pid = 0
      sysusergroup_item.name = 'super'
      sysusergroup_item.rules = {'permissions': ['all']}
      sysusergroup_item.access = {'permissions': ['all']}
      sysusergroup_item.status = 'normal'
      sysusergroup_item.created_at = datetime.fromisoformat('2024-04-05T12:15:11')
      sysusergroup_item.updated_at = datetime.fromisoformat('2025-11-19T09:29:53')
      db.add(sysusergroup_item)

def import_SysGeneralConfig(db: Session):
    """导入 SysGeneralConfig 数据"""
    if 'sys_general_config' not in inspector.get_table_names():
        print('🔧 创建表: sys_general_config')
        SysGeneralConfig.__table__.create(bind=engine)
    else:
        print('✅ 表已存在: sys_general_config')
    if not table_has_data(db, SysGeneralConfig):
      print('📥 导入数据: SysGeneralConfig')
      sysgeneralconfig_item = SysGeneralConfig()  # noqa: F821
      sysgeneralconfig_item.id = 1
      sysgeneralconfig_item.name = 'name'
      sysgeneralconfig_item.group = 'basic'
      sysgeneralconfig_item.title = 'Site name'
      sysgeneralconfig_item.tip = 'Please Input  Site name'
      sysgeneralconfig_item.type = 'string'
      sysgeneralconfig_item.visible = ''
      sysgeneralconfig_item.value = '栈鱼后台管理系统Pro 1.0'
      sysgeneralconfig_item.content = ''
      sysgeneralconfig_item.rule = 'required'
      sysgeneralconfig_item.extend = ''
      sysgeneralconfig_item.setting = ''
      sysgeneralconfig_item.created_at = datetime.fromisoformat('2024-12-29T01:39:29')
      sysgeneralconfig_item.updated_at = datetime.fromisoformat('2024-12-27T11:57:06')
      db.add(sysgeneralconfig_item)
      sysgeneralconfig_item = SysGeneralConfig()  # noqa: F821
      sysgeneralconfig_item.id = 2
      sysgeneralconfig_item.name = 'copyright'
      sysgeneralconfig_item.group = 'basic'
      sysgeneralconfig_item.title = 'Copyright'
      sysgeneralconfig_item.tip = 'Please Input  Copyright'
      sysgeneralconfig_item.type = 'string'
      sysgeneralconfig_item.visible = ''
      sysgeneralconfig_item.value = 'Copyright © 2024 <a href="https://zayum.com" class="text-subtitle-2">栈鱼后台管理系统 1.0</a>. All rights reserved.'
      sysgeneralconfig_item.content = ''
      sysgeneralconfig_item.rule = ''
      sysgeneralconfig_item.extend = ''
      sysgeneralconfig_item.setting = ''
      sysgeneralconfig_item.created_at = datetime.fromisoformat('2024-12-29T01:39:29')
      sysgeneralconfig_item.updated_at = datetime.fromisoformat('2024-12-27T11:57:06')
      db.add(sysgeneralconfig_item)
      sysgeneralconfig_item = SysGeneralConfig()  # noqa: F821
      sysgeneralconfig_item.id = 3
      sysgeneralconfig_item.name = 'cdnurl'
      sysgeneralconfig_item.group = 'basic'
      sysgeneralconfig_item.title = 'Cdn url'
      sysgeneralconfig_item.tip = 'Please Input  Site name'
      sysgeneralconfig_item.type = 'string'
      sysgeneralconfig_item.visible = ''
      sysgeneralconfig_item.value = 'https://zhanor.com'
      sysgeneralconfig_item.content = ''
      sysgeneralconfig_item.rule = ''
      sysgeneralconfig_item.extend = ''
      sysgeneralconfig_item.setting = ''
      sysgeneralconfig_item.created_at = datetime.fromisoformat('2024-12-29T01:39:29')
      sysgeneralconfig_item.updated_at = datetime.fromisoformat('2024-12-27T11:57:06')
      db.add(sysgeneralconfig_item)
      sysgeneralconfig_item = SysGeneralConfig()  # noqa: F821
      sysgeneralconfig_item.id = 4
      sysgeneralconfig_item.name = 'version'
      sysgeneralconfig_item.group = 'basic'
      sysgeneralconfig_item.title = 'Version'
      sysgeneralconfig_item.tip = 'Please Input  Version'
      sysgeneralconfig_item.type = 'string'
      sysgeneralconfig_item.visible = ''
      sysgeneralconfig_item.value = '1.0.1'
      sysgeneralconfig_item.content = ''
      sysgeneralconfig_item.rule = 'required'
      sysgeneralconfig_item.extend = ''
      sysgeneralconfig_item.setting = ''
      sysgeneralconfig_item.created_at = datetime.fromisoformat('2024-12-29T01:39:29')
      sysgeneralconfig_item.updated_at = datetime.fromisoformat('2024-12-27T11:57:06')
      db.add(sysgeneralconfig_item)
      sysgeneralconfig_item = SysGeneralConfig()  # noqa: F821
      sysgeneralconfig_item.id = 5
      sysgeneralconfig_item.name = 'timezone'
      sysgeneralconfig_item.group = 'basic'
      sysgeneralconfig_item.title = 'Timezone'
      sysgeneralconfig_item.tip = ''
      sysgeneralconfig_item.type = 'string'
      sysgeneralconfig_item.visible = ''
      sysgeneralconfig_item.value = 'Asia/Shanghai'
      sysgeneralconfig_item.content = ''
      sysgeneralconfig_item.rule = 'required'
      sysgeneralconfig_item.extend = ''
      sysgeneralconfig_item.setting = ''
      sysgeneralconfig_item.created_at = datetime.fromisoformat('2024-12-29T01:39:29')
      sysgeneralconfig_item.updated_at = datetime.fromisoformat('2024-12-27T11:57:06')
      db.add(sysgeneralconfig_item)
      sysgeneralconfig_item = SysGeneralConfig()  # noqa: F821
      sysgeneralconfig_item.id = 6
      sysgeneralconfig_item.name = 'forbiddenip'
      sysgeneralconfig_item.group = 'basic'
      sysgeneralconfig_item.title = 'Forbidden ip'
      sysgeneralconfig_item.tip = 'Please Input  Forbidden ip'
      sysgeneralconfig_item.type = 'text'
      sysgeneralconfig_item.visible = ''
      sysgeneralconfig_item.value = '12.23.21.1\n1.2.3.6\n34.78.43.1'
      sysgeneralconfig_item.content = ''
      sysgeneralconfig_item.rule = ''
      sysgeneralconfig_item.extend = ''
      sysgeneralconfig_item.setting = ''
      sysgeneralconfig_item.created_at = datetime.fromisoformat('2025-04-29T07:12:13')
      sysgeneralconfig_item.updated_at = datetime.fromisoformat('2025-04-29T07:12:13')
      db.add(sysgeneralconfig_item)
      sysgeneralconfig_item = SysGeneralConfig()  # noqa: F821
      sysgeneralconfig_item.id = 7
      sysgeneralconfig_item.name = 'languages'
      sysgeneralconfig_item.group = 'basic'
      sysgeneralconfig_item.title = 'Languages'
      sysgeneralconfig_item.tip = ''
      sysgeneralconfig_item.type = 'array'
      sysgeneralconfig_item.visible = ''
      sysgeneralconfig_item.value = '{"frontend": "zh-cn", "backend": "zh-cn"}'
      sysgeneralconfig_item.content = ''
      sysgeneralconfig_item.rule = 'required'
      sysgeneralconfig_item.extend = ''
      sysgeneralconfig_item.setting = ''
      sysgeneralconfig_item.created_at = datetime.fromisoformat('2024-12-29T01:39:29')
      sysgeneralconfig_item.updated_at = datetime.fromisoformat('2024-12-29T01:39:29')
      db.add(sysgeneralconfig_item)
      sysgeneralconfig_item = SysGeneralConfig()  # noqa: F821
      sysgeneralconfig_item.id = 8
      sysgeneralconfig_item.name = 'fixedpage'
      sysgeneralconfig_item.group = 'basic'
      sysgeneralconfig_item.title = 'Fixed page'
      sysgeneralconfig_item.tip = 'Please Input Fixed page'
      sysgeneralconfig_item.type = 'string'
      sysgeneralconfig_item.visible = ''
      sysgeneralconfig_item.value = 'dashboard'
      sysgeneralconfig_item.content = ''
      sysgeneralconfig_item.rule = 'required'
      sysgeneralconfig_item.extend = ''
      sysgeneralconfig_item.setting = ''
      sysgeneralconfig_item.created_at = datetime.fromisoformat('2024-12-29T01:39:29')
      sysgeneralconfig_item.updated_at = datetime.fromisoformat('2024-12-27T11:57:06')
      db.add(sysgeneralconfig_item)
      sysgeneralconfig_item = SysGeneralConfig()  # noqa: F821
      sysgeneralconfig_item.id = 9
      sysgeneralconfig_item.name = 'categorytype'
      sysgeneralconfig_item.group = 'dictionary'
      sysgeneralconfig_item.title = 'Category type'
      sysgeneralconfig_item.tip = ''
      sysgeneralconfig_item.type = 'array'
      sysgeneralconfig_item.visible = ''
      sysgeneralconfig_item.value = '{"default": "Default", "page": "Page", "article": "Article"}'
      sysgeneralconfig_item.content = ''
      sysgeneralconfig_item.rule = ''
      sysgeneralconfig_item.extend = ''
      sysgeneralconfig_item.setting = ''
      sysgeneralconfig_item.created_at = datetime.fromisoformat('2024-12-29T01:39:29')
      sysgeneralconfig_item.updated_at = datetime.fromisoformat('2024-12-27T11:57:06')
      db.add(sysgeneralconfig_item)
      sysgeneralconfig_item = SysGeneralConfig()  # noqa: F821
      sysgeneralconfig_item.id = 10
      sysgeneralconfig_item.name = 'default_category'
      sysgeneralconfig_item.group = 'dictionary'
      sysgeneralconfig_item.title = 'Default Category'
      sysgeneralconfig_item.tip = ''
      sysgeneralconfig_item.type = 'array'
      sysgeneralconfig_item.visible = ''
      sysgeneralconfig_item.value = '{"default": "Default"}'
      sysgeneralconfig_item.content = ''
      sysgeneralconfig_item.rule = ''
      sysgeneralconfig_item.extend = ''
      sysgeneralconfig_item.setting = ''
      sysgeneralconfig_item.created_at = datetime.fromisoformat('2024-12-29T01:39:29')
      sysgeneralconfig_item.updated_at = datetime.fromisoformat('2024-12-27T11:57:06')
      db.add(sysgeneralconfig_item)
      sysgeneralconfig_item = SysGeneralConfig()  # noqa: F821
      sysgeneralconfig_item.id = 11
      sysgeneralconfig_item.name = 'mail_type'
      sysgeneralconfig_item.group = 'email'
      sysgeneralconfig_item.title = 'Mail type'
      sysgeneralconfig_item.tip = 'Please Input Mail type'
      sysgeneralconfig_item.type = 'select'
      sysgeneralconfig_item.visible = ''
      sysgeneralconfig_item.value = 'SMTP'
      sysgeneralconfig_item.content = '["Please Select","SMTP"]'
      sysgeneralconfig_item.rule = ''
      sysgeneralconfig_item.extend = ''
      sysgeneralconfig_item.setting = ''
      sysgeneralconfig_item.created_at = datetime.fromisoformat('2024-12-29T01:39:29')
      sysgeneralconfig_item.updated_at = datetime.fromisoformat('2024-12-29T20:59:28')
      db.add(sysgeneralconfig_item)
      sysgeneralconfig_item = SysGeneralConfig()  # noqa: F821
      sysgeneralconfig_item.id = 12
      sysgeneralconfig_item.name = 'mail_smtp_host'
      sysgeneralconfig_item.group = 'email'
      sysgeneralconfig_item.title = 'Mail smtp host'
      sysgeneralconfig_item.tip = 'Please Input Mail smtp host'
      sysgeneralconfig_item.type = 'string'
      sysgeneralconfig_item.visible = ''
      sysgeneralconfig_item.value = 'smtp.qq.com'
      sysgeneralconfig_item.content = ''
      sysgeneralconfig_item.rule = ''
      sysgeneralconfig_item.extend = ''
      sysgeneralconfig_item.setting = ''
      sysgeneralconfig_item.created_at = datetime.fromisoformat('2024-12-29T01:39:29')
      sysgeneralconfig_item.updated_at = datetime.fromisoformat('2024-12-27T11:57:06')
      db.add(sysgeneralconfig_item)
      sysgeneralconfig_item = SysGeneralConfig()  # noqa: F821
      sysgeneralconfig_item.id = 13
      sysgeneralconfig_item.name = 'mail_smtp_port'
      sysgeneralconfig_item.group = 'email'
      sysgeneralconfig_item.title = 'Mail smtp port'
      sysgeneralconfig_item.tip = 'Please Input  Mail smtp port(default25,SSL：465,TLS：587)'
      sysgeneralconfig_item.type = 'string'
      sysgeneralconfig_item.visible = ''
      sysgeneralconfig_item.value = '465'
      sysgeneralconfig_item.content = ''
      sysgeneralconfig_item.rule = ''
      sysgeneralconfig_item.extend = ''
      sysgeneralconfig_item.setting = ''
      sysgeneralconfig_item.created_at = datetime.fromisoformat('2024-12-29T01:39:29')
      sysgeneralconfig_item.updated_at = datetime.fromisoformat('2024-12-27T11:57:06')
      db.add(sysgeneralconfig_item)
      sysgeneralconfig_item = SysGeneralConfig()  # noqa: F821
      sysgeneralconfig_item.id = 14
      sysgeneralconfig_item.name = 'mail_smtp_user'
      sysgeneralconfig_item.group = 'email'
      sysgeneralconfig_item.title = 'Mail smtp user'
      sysgeneralconfig_item.tip = 'Please Input Mail smtp user'
      sysgeneralconfig_item.type = 'string'
      sysgeneralconfig_item.visible = ''
      sysgeneralconfig_item.value = '10000'
      sysgeneralconfig_item.content = ''
      sysgeneralconfig_item.rule = ''
      sysgeneralconfig_item.extend = ''
      sysgeneralconfig_item.setting = ''
      sysgeneralconfig_item.created_at = datetime.fromisoformat('2024-12-29T01:39:29')
      sysgeneralconfig_item.updated_at = datetime.fromisoformat('2024-12-27T11:57:06')
      db.add(sysgeneralconfig_item)
      sysgeneralconfig_item = SysGeneralConfig()  # noqa: F821
      sysgeneralconfig_item.id = 15
      sysgeneralconfig_item.name = 'mail_smtp_pass'
      sysgeneralconfig_item.group = 'email'
      sysgeneralconfig_item.title = 'Mail smtp password'
      sysgeneralconfig_item.tip = 'Please Input  Mail smtp password'
      sysgeneralconfig_item.type = 'string'
      sysgeneralconfig_item.visible = ''
      sysgeneralconfig_item.value = 'password'
      sysgeneralconfig_item.content = ''
      sysgeneralconfig_item.rule = ''
      sysgeneralconfig_item.extend = ''
      sysgeneralconfig_item.setting = ''
      sysgeneralconfig_item.created_at = datetime.fromisoformat('2024-12-29T01:39:29')
      sysgeneralconfig_item.updated_at = datetime.fromisoformat('2024-12-27T11:57:06')
      db.add(sysgeneralconfig_item)
      sysgeneralconfig_item = SysGeneralConfig()  # noqa: F821
      sysgeneralconfig_item.id = 16
      sysgeneralconfig_item.name = 'mail_verify_type'
      sysgeneralconfig_item.group = 'email'
      sysgeneralconfig_item.title = 'Mail vertify type'
      sysgeneralconfig_item.tip = 'Please Input Mail vertify type'
      sysgeneralconfig_item.type = 'select'
      sysgeneralconfig_item.visible = ''
      sysgeneralconfig_item.value = 'TLS'
      sysgeneralconfig_item.content = '["None","TLS","SSL"]'
      sysgeneralconfig_item.rule = ''
      sysgeneralconfig_item.extend = ''
      sysgeneralconfig_item.setting = ''
      sysgeneralconfig_item.created_at = datetime.fromisoformat('2024-12-29T01:39:29')
      sysgeneralconfig_item.updated_at = datetime.fromisoformat('2024-12-29T20:58:05')
      db.add(sysgeneralconfig_item)
      sysgeneralconfig_item = SysGeneralConfig()  # noqa: F821
      sysgeneralconfig_item.id = 17
      sysgeneralconfig_item.name = 'mail_from'
      sysgeneralconfig_item.group = 'email'
      sysgeneralconfig_item.title = 'Mail from'
      sysgeneralconfig_item.tip = ''
      sysgeneralconfig_item.type = 'string'
      sysgeneralconfig_item.visible = ''
      sysgeneralconfig_item.value = '10000@qq.com'
      sysgeneralconfig_item.content = ''
      sysgeneralconfig_item.rule = ''
      sysgeneralconfig_item.extend = ''
      sysgeneralconfig_item.setting = ''
      sysgeneralconfig_item.created_at = datetime.fromisoformat('2024-12-29T01:39:29')
      sysgeneralconfig_item.updated_at = datetime.fromisoformat('2024-12-27T11:57:06')
      db.add(sysgeneralconfig_item)
      sysgeneralconfig_item = SysGeneralConfig()  # noqa: F821
      sysgeneralconfig_item.id = 18
      sysgeneralconfig_item.name = 'image_category'
      sysgeneralconfig_item.group = 'dictionary'
      sysgeneralconfig_item.title = 'Attachment Image category'
      sysgeneralconfig_item.tip = ''
      sysgeneralconfig_item.type = 'array'
      sysgeneralconfig_item.visible = ''
      sysgeneralconfig_item.value = '{"default": "Default", "blog": "Blog"}'
      sysgeneralconfig_item.content = ''
      sysgeneralconfig_item.rule = ''
      sysgeneralconfig_item.extend = ''
      sysgeneralconfig_item.setting = ''
      sysgeneralconfig_item.created_at = datetime.fromisoformat('2024-12-29T01:39:29')
      sysgeneralconfig_item.updated_at = datetime.fromisoformat('2024-12-29T01:39:29')
      db.add(sysgeneralconfig_item)
      sysgeneralconfig_item = SysGeneralConfig()  # noqa: F821
      sysgeneralconfig_item.id = 19
      sysgeneralconfig_item.name = 'file_category'
      sysgeneralconfig_item.group = 'dictionary'
      sysgeneralconfig_item.title = 'Attachment File category'
      sysgeneralconfig_item.tip = ''
      sysgeneralconfig_item.type = 'array'
      sysgeneralconfig_item.visible = ''
      sysgeneralconfig_item.value = '{"default": "Default", "product": "Product"}'
      sysgeneralconfig_item.content = ''
      sysgeneralconfig_item.rule = ''
      sysgeneralconfig_item.extend = ''
      sysgeneralconfig_item.setting = ''
      sysgeneralconfig_item.created_at = datetime.fromisoformat('2024-12-29T01:39:29')
      sysgeneralconfig_item.updated_at = datetime.fromisoformat('2024-12-29T01:39:29')
      db.add(sysgeneralconfig_item)
      sysgeneralconfig_item = SysGeneralConfig()  # noqa: F821
      sysgeneralconfig_item.id = 20
      sysgeneralconfig_item.name = 'video_category'
      sysgeneralconfig_item.group = 'dictionary'
      sysgeneralconfig_item.title = 'Attachment Video category'
      sysgeneralconfig_item.tip = ''
      sysgeneralconfig_item.type = 'array'
      sysgeneralconfig_item.visible = ''
      sysgeneralconfig_item.value = '{"default": "Default", "tutorial": "Tutorial"}'
      sysgeneralconfig_item.content = ''
      sysgeneralconfig_item.rule = ''
      sysgeneralconfig_item.extend = ''
      sysgeneralconfig_item.setting = ''
      sysgeneralconfig_item.created_at = datetime.fromisoformat('2024-12-29T01:39:29')
      sysgeneralconfig_item.updated_at = datetime.fromisoformat('2024-12-29T01:39:29')
      db.add(sysgeneralconfig_item)
      sysgeneralconfig_item = SysGeneralConfig()  # noqa: F821
      sysgeneralconfig_item.id = 21
      sysgeneralconfig_item.name = 'audio_category'
      sysgeneralconfig_item.group = 'dictionary'
      sysgeneralconfig_item.title = 'Attachment Audio category'
      sysgeneralconfig_item.tip = ''
      sysgeneralconfig_item.type = 'array'
      sysgeneralconfig_item.visible = ''
      sysgeneralconfig_item.value = '{"default": "Default", "music": "Music"}'
      sysgeneralconfig_item.content = ''
      sysgeneralconfig_item.rule = ''
      sysgeneralconfig_item.extend = ''
      sysgeneralconfig_item.setting = ''
      sysgeneralconfig_item.created_at = datetime.fromisoformat('2024-12-29T01:39:29')
      sysgeneralconfig_item.updated_at = datetime.fromisoformat('2024-12-29T01:39:29')
      db.add(sysgeneralconfig_item)
      sysgeneralconfig_item = SysGeneralConfig()  # noqa: F821
      sysgeneralconfig_item.id = 22
      sysgeneralconfig_item.name = 'document_category'
      sysgeneralconfig_item.group = 'dictionary'
      sysgeneralconfig_item.title = 'Attachment Document category'
      sysgeneralconfig_item.tip = ''
      sysgeneralconfig_item.type = 'array'
      sysgeneralconfig_item.visible = ''
      sysgeneralconfig_item.value = '{"default": "Default", "contract": "Contract"}'
      sysgeneralconfig_item.content = ''
      sysgeneralconfig_item.rule = ''
      sysgeneralconfig_item.extend = ''
      sysgeneralconfig_item.setting = ''
      sysgeneralconfig_item.created_at = datetime.fromisoformat('2024-12-29T01:39:29')
      sysgeneralconfig_item.updated_at = datetime.fromisoformat('2024-12-29T01:39:29')
      db.add(sysgeneralconfig_item)
      sysgeneralconfig_item = SysGeneralConfig()  # noqa: F821
      sysgeneralconfig_item.id = 23
      sysgeneralconfig_item.name = 'user_page_title'
      sysgeneralconfig_item.group = 'user'
      sysgeneralconfig_item.title = 'User Page Title'
      sysgeneralconfig_item.tip = 'User Page Title'
      sysgeneralconfig_item.type = 'string'
      sysgeneralconfig_item.visible = ''
      sysgeneralconfig_item.value = 'User Center'
      sysgeneralconfig_item.content = ''
      sysgeneralconfig_item.rule = 'letters'
      sysgeneralconfig_item.extend = ''
      sysgeneralconfig_item.setting = ''
      sysgeneralconfig_item.created_at = datetime.fromisoformat('2024-12-29T01:39:29')
      sysgeneralconfig_item.updated_at = datetime.fromisoformat('2024-12-30T12:50:59')
      db.add(sysgeneralconfig_item)
      sysgeneralconfig_item = SysGeneralConfig()  # noqa: F821
      sysgeneralconfig_item.id = 24
      sysgeneralconfig_item.name = 'user_footer'
      sysgeneralconfig_item.group = 'user'
      sysgeneralconfig_item.title = 'User Center Footer'
      sysgeneralconfig_item.tip = 'User Center Footer'
      sysgeneralconfig_item.type = 'text'
      sysgeneralconfig_item.visible = ''
      sysgeneralconfig_item.value = 'Copyright © 2024 <a href="https://zayum.com" class="link-secondary">会员中心</a>. All rights reserved.'
      sysgeneralconfig_item.content = ''
      sysgeneralconfig_item.rule = 'required'
      sysgeneralconfig_item.extend = ''
      sysgeneralconfig_item.setting = ''
      sysgeneralconfig_item.created_at = datetime.fromisoformat('2024-12-29T01:39:29')
      sysgeneralconfig_item.updated_at = datetime.fromisoformat('2024-12-30T12:50:59')
      db.add(sysgeneralconfig_item)


def run_all():
    db = SessionLocal()
    try:
        import_SysAdmin(db)
        import_SysUserBalanceLog(db)
        import_SysAttachment(db)
        import_SysGeneralCategory(db)
        import_SysAdminRule(db)
        import_SysNotification(db)
        import_SysAdminLog(db)
        import_SysUserRule(db)
        import_SysAdminGroup(db)
        import_SysPlugin(db)
        import_SysUser(db)
        import_SysUserScoreLog(db)
        import_SysAnalyticsSummary(db)
        import_SysAttachmentCategory(db)
        import_SysUserGroup(db)
        import_SysGeneralConfig(db)
        db.commit()
    finally:
        db.close()

if __name__ == '__main__':
    run_all()