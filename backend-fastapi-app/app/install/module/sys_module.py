from datetime import datetime, date
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import inspect, create_engine, select
from app.dependencies.database import engine
from app.models.sys_admin import SysAdmin as SysAdminType
from app.models.sys_admin_group import SysAdminGroup as SysAdminGroupType
from app.models.sys_admin_log import SysAdminLog as SysAdminLogType
from app.models.sys_admin_rule import SysAdminRule as SysAdminRuleType
from app.models.sys_plugin import SysPlugin as SysPluginType

# Type aliases
SysAdmin: type[SysAdminType] = SysAdminType
SysAdminGroup: type[SysAdminGroupType] = SysAdminGroupType
SysAdminLog: type[SysAdminLogType] = SysAdminLogType
SysAdminRule: type[SysAdminRuleType] = SysAdminRuleType
SysPlugin: type[SysPluginType] = SysPluginType


def import_SysAdmin(db: Session, inspector):
    """导入 SysAdmin 数据"""
    if "sys_admin" not in inspector.get_table_names():
        print("🔧 创建表: sys_admin")
        SysAdmin.__table__.create(bind=engine)
    else:
        print("✅ 表已存在: sys_admin")
    if db.scalar(select(SysAdmin).limit(1)) is None:
        print("📥 导入数据: SysAdmin")
        admin = SysAdmin()
        admin.id = 1
        admin.group_id = 1
        admin.username = "admin"
        admin.nickname = "SupperAdmin"
        admin._password = "$2b$12$cw3xuR7n.Cid4CZdchXIp.x0H4t5SKKDOq06lwZOhfAxCAd7Pi3p6"
        admin.avatar = None
        admin.email = "13800000000@qq.com"
        admin.mobile = "13800000000"
        admin.login_failure = 0
        admin.login_at = datetime.fromisoformat("2025-06-25T23:02:17")
        admin.login_ip = "127.0.0.1"
        admin.token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzUxNDk3MzM2fQ.BmJsP6wIBWutRfScL6rOgdPGV4eoBNmPaBNcHVm-jgs"
        admin.status = "normal"
        admin.created_at = datetime.fromisoformat("2025-05-15T23:49:04")
        admin.updated_at = datetime.fromisoformat("2025-06-25T23:02:17")
        db.add(admin)


def import_SysAdminGroup(db: Session, inspector):
    """导入 SysAdminGroup 数据"""
    if "sys_admin_group" not in inspector.get_table_names():
        print("🔧 创建表: sys_admin_group")
        SysAdminGroup.__table__.create(bind=engine)
    else:
        print("✅ 表已存在: sys_admin_group")
    if db.scalar(select(SysAdminGroup).limit(1)) is None:
        print("📥 导入数据: SysAdminGroup")
        group = SysAdminGroup()
        group.id = 1
        group.pid = 1
        group.name = "super"
        group.rules = ["all"]
        group.access = ["all"]
        group.status = "normal"
        group.created_at = datetime.fromisoformat("2024-04-05T12:15:11")
        group.updated_at = datetime.fromisoformat("2025-03-04T15:54:49")
        db.add(group)


def import_SysAdminLog(db: Session, inspector):
    """导入 SysAdminLog 数据"""
    if "sys_admin_log" not in inspector.get_table_names():
        print("🔧 创建表: sys_admin_log")
        SysAdminLog.__table__.create(bind=engine)
    else:
        print("✅ 表已存在: sys_admin_log")
    print("ℹ️  表 sys_admin_log 无初始数据，无需导入")


def import_SysAdminRule(db: Session, inspector):
    """导入 SysAdminRule 数据"""
    if "sys_admin_rule" not in inspector.get_table_names():
        print("🔧 创建表: sys_admin_rule")
        SysAdminRule.__table__.create(bind=engine)
    else:
        print("✅ 表已存在: sys_admin_rule")
    if db.scalar(select(SysAdminRule).limit(1)) is None:
        print("📥 导入数据: SysAdminRule")
        rules = [
            (1, 'menu', 0, 'dashboard', '/admin', '/_core/dashboard/dashboard', '/dashboard',
             {"icon": "mdi:view-dashboard-outline", "title": "dashboard.dashboard"}, "{}", 'addtabs', 'Dashboard', None, 1, 'normal', '2024-01-22 14:32:00', '2025-03-04 10:59:45'),
            (2, 'menu', 1, 'workspace', '/dashboard/workspace', '/_core/dashboard/workspace/index', None, {"icon": "mdi:view-dashboard-outline", "title": "dashboard.workspace.workspace"}, {
             "view": True}, 'addtabs', 'Dashboard', None, 1, 'normal', '2024-01-22 14:32:00', '2025-06-05 00:22:17'),
            (3, 'menu', 0, 'generals', '/generals', None, None, {"icon": "mdi:cog-outline", "title": "general.general"},
             "{}", 'addtabs', 'Generals', None, 2, 'normal', '2024-01-22 14:32:00', '2025-02-28 18:40:34'),
            (4, 'menu', 3, 'general.profile', '/general/profile', '/_core/general/profile', None, {"icon": "mdi:account-outline", "title": "general.profile.profile"}, {
             "edit": True}, 'addtabs', 'GeneralProfile', None, 11, 'normal', '2024-01-22 14:32:00', '2025-02-28 12:04:00'),
            (5, 'menu', 3, 'general.category', '/general/category', '/_core/general/category', '', {"icon": "mdi:category-plus-outline", "title": "general.category.category", "menuVisibleWithForbidden": "false"}, {
             "add": True, "edit": True, "view": True, "delete": True}, 'ajax', 'GeneralsCategory', None, 0, 'normal', '2025-03-04 03:24:40', '2025-03-07 11:12:12'),
            (6, 'menu', 3, 'general.config', '/general/config', '/_core/general/config', None, {"icon": "mdi:cog-outline", "title": "general.config.config"}, {
             "add": True, "edit": True, "delete": True}, 'addtabs', 'GeneralConfig', None, 8, 'normal', '2024-01-22 14:32:00', '2025-03-04 07:36:31'),
            (7, 'menu', 0, 'attachments', '/attachments', None, None,
             {"icon": "mdi:paperclip", "title": "attachment.attachment_manage"}, "{}", 'blank', 'Attachment', None, 9, 'normal', '2024-01-22 14:32:00', '2025-03-06 11:39:00'),
            (8, 'menu', 7, 'attachment.attachment', '/attachment/attachment', '/_core/attachment/attachment', None, {"icon": "mdi:file-outline", "title": "attachment.attachment"}, {
             "add": True, "edit": True, "view": True, "delete": True}, 'addtabs', 'Attachment', None, 10, 'normal', '2024-01-22 14:32:00', '2025-03-06 11:39:00'),
            (9, 'menu', 0, 'plugins', '/plugins', None, None, {"icon": "mdi:puzzle-outline", "title": "plugin.plugin",
             "childComponent": "/_core/general/profile"}, "{}", 'addtabs', 'Plugin', None, 3, 'normal', '2024-01-22 14:32:00', '2025-02-28 17:51:12'),
            (10, 'menu', 0, 'admin', '/admin', None, None, {"icon": "mdi:shield-account-outline", "title": "admin.admin.field.admin"},
             "{}", 'addtabs', 'Admin', None, 4, 'normal', '2024-01-22 14:32:00', '2025-06-04 12:15:36'),
            (11, 'menu', 10, 'admin.admin', '/admin/admin', '/_core/admin/admin', None, {"icon": "mdi:account-outline", "title": "admin.admin.admin_manage"}, {
             "add": True, "ajax": True, "edit": True, "view": True, "delete": True}, 'addtabs', 'Admin', None, 20, 'normal', '2024-01-22 14:32:00', '2025-03-06 16:24:24'),
            (12, 'menu', 10, 'admin.group', '/admin/group', '/_core/admin/group', None, {"icon": "mdi:account-group-outline", "title": "admin.group.group"}, {
             "add": True, "ajax": True, "edit": True, "view": True, "delete": True}, 'addtabs', 'AdminGroup', None, 21, 'normal', '2024-01-22 14:32:00', '2025-03-06 13:03:05'),
            (13, 'menu', 10, 'admin.rule', '/admin/rule', '/_core/admin/rule', None, {"icon": "mdi:shield-account-outline", "title": "admin.rule.rule"}, {
             "add": True, "edit": True, "view": True, "delete": True}, 'addtabs', 'AdminRule', None, 47, 'normal', '2024-01-22 14:32:00', '2025-03-06 13:03:05'),
            (14, 'menu', 10, 'admin.log', '/admin/log', '/_core/admin/log', None, {"icon": "mdi:clipboard-text-outline", "title": "admin.log.log"}, {
             "view": True}, 'addtabs', 'AdminLog', None, 50, 'normal', '2024-01-22 14:32:00', '2025-03-04 07:36:31'),
            (15, 'menu', 0, 'users', '/users', None, None, {"icon": "mdi:account-multiple-outline", "title": "user.user"},
             "{}", 'addtabs', 'Users', None, 24, 'normal', '2024-01-22 14:32:00', '2025-02-26 17:47:48'),
            (16, 'menu', 15, 'user', '/user', '/_core/user/user', None, {"icon": "mdi:account-outline", "title": "user.user_manage"}, {
             "add": True, "edit": True, "view": True, "delete": True}, 'addtabs', 'User', None, 24, 'normal', '2024-01-22 14:32:00', '2025-03-06 16:19:59'),
            (17, 'menu', 15, 'user.rule', '/user/rule', '/_core/user/rule', None, {"icon": "mdi:shield-account-outline", "title": "user.rule.rule"}, {
             "add": True, "edit": True, "view": True, "delete": True}, 'addtabs', 'UserRule', None, 26, 'normal', '2024-01-22 14:32:00', '2025-03-04 07:36:31'),
            (18, 'menu', 15, 'user.balance.log', '/user/balance/log', '/_core/user/balance_log', None, {"icon": "mdi:account-balance-wallet-outline", "title": "user.balance_log.balance_log"}, {
             "add": True, "edit": True, "view": True, "delete": True}, 'addtabs', 'UserBalance', None, 25, 'normal', '2024-01-22 14:32:00', '2025-03-06 16:27:28'),
            (19, 'menu', 15, 'user.score.log', '/user/score/log', '/_core/user/score_log', None, {"icon": "mdi:scoreboard-outline", "title": "user.score_log.score_log"}, {
             "add": True, "edit": True, "view": True, "delete": True}, 'addtabs', 'UserScore', None, 25, 'normal', '2024-01-22 14:32:00', '2025-03-06 16:28:37'),
            (20, 'menu', 15, 'user.group', '/user/group', '/_core/user/group', None, {"icon": "mdi:account-group-outline", "title": "user.group.group"}, {
             "add": True, "edit": True, "view": True, "delete": True}, 'addtabs', 'UserGroup', None, 0, 'normal', '2024-09-26 13:01:14', '2025-03-04 07:36:31'),
            (22, 'menu', 9, 'generator', '/plugins/generator', '/plugins/generator', '', {"icon": "mdi:codepen", "title": "generator.code_generator", "menuVisibleWithForbidden": "false"}, {
             "view": True}, 'ajax', 'generator', None, 0, 'normal', '2025-02-28 10:31:33', '2025-03-04 07:36:31'),
            (24, 'menu', 7, 'attachmentCategory', '/attachment/category', '/_core/attachment/category', '', {"icon": "mdi:attachment", "title": "attachment.category.category", "menuVisibleWithForbidden": "false"}, {
             "add": True, "edit": True, "view": True, "delete": True}, 'ajax', 'attachmentCategory', None, 0, 'normal', '2025-03-06 03:54:07', '2025-03-06 12:56:31'),
            (25, 'menu', 9, 'plugin', '/plugin/plugin', '/_core/plugin/plugin', '', {"icon": "mdi:shape-rectangle-add", "title": "plugin.plugin", "menuVisibleWithForbidden": "false"}, {
             "add": True, "edit": True, "view": True, "delete": True}, 'ajax', 'plugin', None, 0, 'normal', '2025-03-09 02:40:04', '2025-03-09 11:05:32'),
            (26, 'menu', 9, 'plugin_store', '/plugin/plugin_store', '/_core/plugin_store', '', {"icon": "mdi:all-inclusive", "title": "plugin.plugin_store", "menuVisibleWithForbidden": "false"}, {
             "enable": True, "disable": True, "install": True, "unstall": True}, 'ajax', 'online_plugin', None, 0, 'normal', '2025-03-10 07:15:54', '2025-03-10 16:07:41'),
            (27, 'menu', 1, 'analytics', '/dashboard/analytics', '/_core/dashboard/analytics/index', None, {"icon": "mdi:view-dashboard-outline", "title": "dashboard.analytics"}, {
             "view": True}, 'addtabs', 'Dashboard', None, 1, 'normal', '2024-01-22 14:32:00', '2025-03-04 07:36:31')
        ]

        for rule_data in rules:
            rule = SysAdminRule()
            rule.id = rule_data[0]
            rule.rule_type = rule_data[1]
            rule.parent_id = rule_data[2]
            rule.name = rule_data[3]
            rule.path = rule_data[4]
            rule.component = rule_data[5]
            rule.redirect = rule_data[6]
            rule.meta = rule_data[7]
            rule.permission = rule_data[8]
            rule.menu_display_type = rule_data[9]
            rule.model_name = rule_data[10]
            rule.deleted_at = rule_data[11]
            rule.weigh = rule_data[12]
            rule.status = rule_data[13]
            rule.created_at = datetime.fromisoformat(rule_data[14])
            rule.updated_at = datetime.fromisoformat(rule_data[15])
            db.add(rule)


def import_SysPlugin(db: Session, inspector):
    """导入 SysPlugin 数据"""
    if "sys_plugin" not in inspector.get_table_names():
        print("🔧 创建表: sys_plugin")
        SysPlugin.__table__.create(bind=engine)
    else:
        print("✅ 表已存在: sys_plugin")
    if db.scalar(select(SysPlugin).limit(1)) is None:
        print("📥 导入数据: SysPlugin")
        plugin = SysPlugin()
        plugin.id = 2
        plugin.title = "代码生成器"
        plugin.author = "StkFish"
        plugin.uuid = "generator"
        plugin.description = "generator"
        plugin.version = "1.0.1"
        plugin.downloads = 12
        plugin.download_url = "2"
        plugin.md5_hash = "2"
        plugin.price = float(Decimal("10"))
        plugin.paid = 0
        plugin.installed = 1
        plugin.enabled = 1
        plugin.setting_menu = "0"
        plugin.status = "normal"
        plugin.created_at = datetime.fromisoformat("2025-03-10T17:09:22")
        plugin.updated_at = datetime.fromisoformat("2025-05-09T09:34:40")
        db.add(plugin)
