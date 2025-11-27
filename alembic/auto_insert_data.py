"""insert initial data"""

from datetime import datetime, date
from decimal import Decimal
from alembic import op
import sqlalchemy as sa

revision = '20251127091909'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    table_sys_admin = sa.table(
        'sys_admin',
        sa.column('id', sa.Integer),
        sa.column('group_id', sa.Integer),
        sa.column('username', sa.String),
        sa.column('nickname', sa.String),
        sa.column('password', sa.String),
        sa.column('avatar', sa.String),
        sa.column('email', sa.String),
        sa.column('mobile', sa.String),
        sa.column('login_failure', sa.Integer),
        sa.column('login_at', sa.DateTime),
        sa.column('login_ip', sa.String),
        sa.column('token', sa.String),
        sa.column('status', sa.Enum),
        sa.column('created_at', sa.DateTime),
        sa.column('updated_at', sa.DateTime),
    )
    op.bulk_insert(table_sys_admin, [
        { 'id': 1, 'group_id': 1, 'username': 'admin', 'nickname': 'SupperAdmin', 'password': '$2b$12$8qJ15oSRtULhh8A/EctDU.MzQm.vyoZRpohknvZqCY5Yr8N9crF4K', 'avatar': '/uploads/avatar/avatar_1_c7b7e5.png', 'email': '13800000000@qq.com', 'mobile': '13800000000', 'login_failure': 0, 'login_at': datetime.fromisoformat('2025-11-24T00:24:46'), 'login_ip': '127.0.0.1', 'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzY0NTQ4Njg1fQ.ecw6ZOPvPYmXQDs7YhGYiLijWd9z40lrgktORS-T22w', 'status': 'normal', 'created_at': datetime.fromisoformat('2025-06-26T02:59:10'), 'updated_at': datetime.fromisoformat('2025-11-24T00:24:46') },
    ])

    table_sys_general_category = sa.table(
        'sys_general_category',
        sa.column('id', sa.Integer),
        sa.column('pid', sa.Integer),
        sa.column('type', sa.String),
        sa.column('name', sa.String),
        sa.column('thumb', sa.String),
        sa.column('keywords', sa.String),
        sa.column('description', sa.String),
        sa.column('weigh', sa.Integer),
        sa.column('status', sa.Enum),
        sa.column('created_at', sa.DateTime),
        sa.column('updated_at', sa.DateTime),
    )
    op.bulk_insert(table_sys_general_category, [
        { 'id': 1, 'pid': 0, 'type': 'default', 'name': 'default', 'thumb': '', 'keywords': '', 'description': '', 'weigh': 0, 'status': 'normal', 'created_at': datetime.fromisoformat('2024-05-08T17:19:06'), 'updated_at': datetime.fromisoformat('2025-03-07T11:50:19') },
        { 'id': 2, 'pid': 0, 'type': 'blog', 'name': 'news', 'thumb': '', 'keywords': '', 'description': '', 'weigh': 0, 'status': 'normal', 'created_at': datetime.fromisoformat('2025-06-04T17:47:14'), 'updated_at': datetime.fromisoformat('2025-06-04T17:47:14') },
    ])

    table_sys_admin_rule = sa.table(
        'sys_admin_rule',
        sa.column('id', sa.Integer),
        sa.column('rule_type', sa.Enum),
        sa.column('parent_id', sa.Integer),
        sa.column('name', sa.String),
        sa.column('path', sa.String),
        sa.column('component', sa.String),
        sa.column('redirect', sa.String),
        sa.column('meta', sa.JSON),
        sa.column('permission', sa.JSON),
        sa.column('menu_display_type', sa.Enum),
        sa.column('model_name', sa.String),
        sa.column('deleted_at', sa.DATETIME),
        sa.column('weigh', sa.Integer),
        sa.column('status', sa.Enum),
        sa.column('created_at', sa.DateTime),
        sa.column('updated_at', sa.DateTime),
    )
    op.bulk_insert(table_sys_admin_rule, [
        { 'id': 1, 'rule_type': 'menu', 'parent_id': 0, 'name': 'dashboard', 'path': '/dashboard/', 'component': '/_core/dashboard/dashboard', 'redirect': '/dashboard', 'meta': '{"icon": "mdi:view-dashboard-outline", "title": "dashboard.dashboard"}', 'permission': '{}', 'menu_display_type': 'addtabs', 'model_name': 'Dashboard', 'deleted_at': None, 'weigh': 1, 'status': 'normal', 'created_at': datetime.fromisoformat('2024-01-22T14:32:00'), 'updated_at': datetime.fromisoformat('2025-11-11T01:23:42') },
        { 'id': 2, 'rule_type': 'menu', 'parent_id': 1, 'name': 'workspace', 'path': '/dashboard/workspace', 'component': '/_core/dashboard/workspace/index', 'redirect': None, 'meta': '{"icon": "mdi:view-dashboard-outline", "title": "dashboard.workspace.workspace"}', 'permission': '{"view": true}', 'menu_display_type': 'addtabs', 'model_name': 'Dashboard', 'deleted_at': None, 'weigh': 1, 'status': 'normal', 'created_at': datetime.fromisoformat('2024-01-22T14:32:00'), 'updated_at': datetime.fromisoformat('2025-06-05T00:22:17') },
        { 'id': 3, 'rule_type': 'menu', 'parent_id': 0, 'name': 'generals', 'path': '/generals', 'component': None, 'redirect': None, 'meta': '{"icon": "mdi:cog-outline", "title": "general.general"}', 'permission': '{}', 'menu_display_type': 'addtabs', 'model_name': 'Generals', 'deleted_at': None, 'weigh': 2, 'status': 'normal', 'created_at': datetime.fromisoformat('2024-01-22T14:32:00'), 'updated_at': datetime.fromisoformat('2025-02-28T18:40:34') },
        { 'id': 4, 'rule_type': 'menu', 'parent_id': 3, 'name': 'general.profile', 'path': '/general/profile', 'component': '/_core/general/profile', 'redirect': None, 'meta': '{"icon": "mdi:account-outline", "title": "general.profile.profile"}', 'permission': '{"edit": true}', 'menu_display_type': 'addtabs', 'model_name': 'GeneralProfile', 'deleted_at': None, 'weigh': 11, 'status': 'normal', 'created_at': datetime.fromisoformat('2024-01-22T14:32:00'), 'updated_at': datetime.fromisoformat('2025-02-28T12:04:00') },
        { 'id': 5, 'rule_type': 'menu', 'parent_id': 3, 'name': 'general.category', 'path': '/general/category', 'component': '/_core/general/category', 'redirect': '', 'meta': '{"icon": "mdi:category-plus-outline", "title": "general.category.category", "menuVisibleWithForbidden": "false"}', 'permission': '{"add": true, "edit": true, "view": true, "delete": true}', 'menu_display_type': 'ajax', 'model_name': 'GeneralsCategory', 'deleted_at': None, 'weigh': 0, 'status': 'normal', 'created_at': datetime.fromisoformat('2025-03-04T03:24:40'), 'updated_at': datetime.fromisoformat('2025-03-07T11:12:12') },
        { 'id': 6, 'rule_type': 'menu', 'parent_id': 3, 'name': 'general.config', 'path': '/general/config', 'component': '/_core/general/config', 'redirect': None, 'meta': '{"icon": "mdi:cog-outline", "title": "general.config.config"}', 'permission': '{"add": true, "edit": true, "delete": true}', 'menu_display_type': 'addtabs', 'model_name': 'GeneralConfig', 'deleted_at': None, 'weigh': 8, 'status': 'normal', 'created_at': datetime.fromisoformat('2024-01-22T14:32:00'), 'updated_at': datetime.fromisoformat('2025-03-04T07:36:31') },
        { 'id': 7, 'rule_type': 'menu', 'parent_id': 0, 'name': 'attachments', 'path': '/attachments', 'component': None, 'redirect': None, 'meta': '{"icon": "mdi:paperclip", "title": "attachment.attachment_manage"}', 'permission': '{}', 'menu_display_type': 'blank', 'model_name': 'Attachment', 'deleted_at': None, 'weigh': 9, 'status': 'normal', 'created_at': datetime.fromisoformat('2024-01-22T14:32:00'), 'updated_at': datetime.fromisoformat('2025-03-06T11:39:00') },
        { 'id': 8, 'rule_type': 'menu', 'parent_id': 7, 'name': 'attachment.attachment', 'path': '/attachment/attachment', 'component': '/_core/attachment/attachment', 'redirect': None, 'meta': '{"icon": "mdi:file-outline", "title": "attachment.attachment"}', 'permission': '{"add": true, "edit": true, "view": true, "delete": true}', 'menu_display_type': 'addtabs', 'model_name': 'Attachment', 'deleted_at': None, 'weigh': 10, 'status': 'normal', 'created_at': datetime.fromisoformat('2024-01-22T14:32:00'), 'updated_at': datetime.fromisoformat('2025-03-06T11:39:00') },
        { 'id': 9, 'rule_type': 'menu', 'parent_id': 0, 'name': 'plugins', 'path': '/plugins', 'component': None, 'redirect': None, 'meta': '{"icon": "mdi:puzzle-outline", "title": "plugin.plugin", "childComponent": "/_core/general/profile"}', 'permission': '{}', 'menu_display_type': 'addtabs', 'model_name': 'Plugin', 'deleted_at': None, 'weigh': 3, 'status': 'normal', 'created_at': datetime.fromisoformat('2024-01-22T14:32:00'), 'updated_at': datetime.fromisoformat('2025-02-28T17:51:12') },
        { 'id': 10, 'rule_type': 'menu', 'parent_id': 0, 'name': 'admin', 'path': '/admin', 'component': None, 'redirect': None, 'meta': '{"icon": "mdi:shield-account-outline", "title": "admin.admin.field.admin"}', 'permission': '{}', 'menu_display_type': 'addtabs', 'model_name': 'Admin', 'deleted_at': None, 'weigh': 4, 'status': 'normal', 'created_at': datetime.fromisoformat('2024-01-22T14:32:00'), 'updated_at': datetime.fromisoformat('2025-06-04T12:15:36') },
        { 'id': 11, 'rule_type': 'menu', 'parent_id': 10, 'name': 'admin.admin', 'path': '/admin/admin', 'component': '/_core/admin/admin', 'redirect': None, 'meta': '{"icon": "mdi:account-outline", "title": "admin.admin.admin_manage"}', 'permission': '{"add": true, "ajax": true, "edit": true, "view": true, "delete": true}', 'menu_display_type': 'addtabs', 'model_name': 'Admin', 'deleted_at': None, 'weigh': 20, 'status': 'normal', 'created_at': datetime.fromisoformat('2024-01-22T14:32:00'), 'updated_at': datetime.fromisoformat('2025-03-06T16:24:24') },
        { 'id': 12, 'rule_type': 'menu', 'parent_id': 10, 'name': 'admin.group', 'path': '/admin/group', 'component': '/_core/admin/group', 'redirect': None, 'meta': '{"icon": "mdi:account-group-outline", "title": "admin.group.group"}', 'permission': '{"add": true, "ajax": true, "edit": true, "view": true, "delete": true}', 'menu_display_type': 'addtabs', 'model_name': 'AdminGroup', 'deleted_at': None, 'weigh': 21, 'status': 'normal', 'created_at': datetime.fromisoformat('2024-01-22T14:32:00'), 'updated_at': datetime.fromisoformat('2025-03-06T13:03:05') },
        { 'id': 13, 'rule_type': 'menu', 'parent_id': 10, 'name': 'admin.rule', 'path': '/admin/rule', 'component': '/_core/admin/rule', 'redirect': None, 'meta': '{"icon": "mdi:shield-account-outline", "title": "admin.rule.rule"}', 'permission': '{"add": true, "edit": true, "view": true, "delete": true}', 'menu_display_type': 'addtabs', 'model_name': 'AdminRule', 'deleted_at': None, 'weigh': 47, 'status': 'normal', 'created_at': datetime.fromisoformat('2024-01-22T14:32:00'), 'updated_at': datetime.fromisoformat('2025-03-06T13:03:05') },
        { 'id': 14, 'rule_type': 'menu', 'parent_id': 10, 'name': 'admin.log', 'path': '/admin/log', 'component': '/_core/admin/log', 'redirect': None, 'meta': '{"icon": "mdi:clipboard-text-outline", "title": "admin.log.log"}', 'permission': '{"view": true}', 'menu_display_type': 'addtabs', 'model_name': 'AdminLog', 'deleted_at': None, 'weigh': 50, 'status': 'normal', 'created_at': datetime.fromisoformat('2024-01-22T14:32:00'), 'updated_at': datetime.fromisoformat('2025-03-04T07:36:31') },
        { 'id': 15, 'rule_type': 'menu', 'parent_id': 0, 'name': 'users', 'path': '/users', 'component': None, 'redirect': None, 'meta': '{"icon": "mdi:account-multiple-outline", "title": "user.user"}', 'permission': '{}', 'menu_display_type': 'addtabs', 'model_name': 'Users', 'deleted_at': None, 'weigh': 24, 'status': 'normal', 'created_at': datetime.fromisoformat('2024-01-22T14:32:00'), 'updated_at': datetime.fromisoformat('2025-02-26T17:47:48') },
        { 'id': 16, 'rule_type': 'menu', 'parent_id': 15, 'name': 'user', 'path': '/user', 'component': '/_core/user/user', 'redirect': None, 'meta': '{"icon": "mdi:account-outline", "title": "user.user_manage"}', 'permission': '{"add": true, "edit": true, "view": true, "delete": true}', 'menu_display_type': 'addtabs', 'model_name': 'User', 'deleted_at': None, 'weigh': 24, 'status': 'normal', 'created_at': datetime.fromisoformat('2024-01-22T14:32:00'), 'updated_at': datetime.fromisoformat('2025-03-06T16:19:59') },
        { 'id': 17, 'rule_type': 'menu', 'parent_id': 15, 'name': 'user.rule', 'path': '/user/rule', 'component': '/_core/user/rule', 'redirect': None, 'meta': '{"icon": "mdi:shield-account-outline", "title": "user.rule.rule"}', 'permission': '{"add": true, "edit": true, "view": true, "delete": true}', 'menu_display_type': 'addtabs', 'model_name': 'UserRule', 'deleted_at': None, 'weigh': 26, 'status': 'normal', 'created_at': datetime.fromisoformat('2024-01-22T14:32:00'), 'updated_at': datetime.fromisoformat('2025-03-04T07:36:31') },
        { 'id': 18, 'rule_type': 'menu', 'parent_id': 15, 'name': 'user.balance.log', 'path': '/user/balance/log', 'component': '/_core/user/balance_log', 'redirect': None, 'meta': '{"icon": "mdi:account-balance-wallet-outline", "title": "user.balance_log.balance_log"}', 'permission': '{"add": true, "edit": true, "view": true, "delete": true}', 'menu_display_type': 'addtabs', 'model_name': 'UserBalance', 'deleted_at': None, 'weigh': 25, 'status': 'normal', 'created_at': datetime.fromisoformat('2024-01-22T14:32:00'), 'updated_at': datetime.fromisoformat('2025-03-06T16:27:28') },
        { 'id': 19, 'rule_type': 'menu', 'parent_id': 15, 'name': 'user.score.log', 'path': '/user/score/log', 'component': '/_core/user/score_log', 'redirect': None, 'meta': '{"icon": "mdi:scoreboard-outline", "title": "user.score_log.score_log"}', 'permission': '{"add": true, "edit": true, "view": true, "delete": true}', 'menu_display_type': 'addtabs', 'model_name': 'UserScore', 'deleted_at': None, 'weigh': 25, 'status': 'normal', 'created_at': datetime.fromisoformat('2024-01-22T14:32:00'), 'updated_at': datetime.fromisoformat('2025-03-06T16:28:37') },
        { 'id': 20, 'rule_type': 'menu', 'parent_id': 15, 'name': 'user.group', 'path': '/user/group', 'component': '/_core/user/group', 'redirect': None, 'meta': '{"icon": "mdi:account-group-outline", "title": "user.group.group"}', 'permission': '{"add": true, "edit": true, "view": true, "delete": true}', 'menu_display_type': 'addtabs', 'model_name': 'UserGroup', 'deleted_at': None, 'weigh': 0, 'status': 'normal', 'created_at': datetime.fromisoformat('2024-09-26T13:01:14'), 'updated_at': datetime.fromisoformat('2025-03-04T07:36:31') },
        { 'id': 22, 'rule_type': 'menu', 'parent_id': 9, 'name': 'generator', 'path': '/plugins/generator', 'component': '/plugins/generator', 'redirect': '', 'meta': '{"icon": "mdi:codepen", "title": "generator.code_generator", "menuVisibleWithForbidden": "false"}', 'permission': '{"view": true}', 'menu_display_type': 'ajax', 'model_name': 'generator', 'deleted_at': None, 'weigh': 0, 'status': 'normal', 'created_at': datetime.fromisoformat('2025-02-28T10:31:33'), 'updated_at': datetime.fromisoformat('2025-03-04T07:36:31') },
        { 'id': 24, 'rule_type': 'menu', 'parent_id': 7, 'name': 'attachmentCategory', 'path': '/attachment/category', 'component': '/_core/attachment/category', 'redirect': '', 'meta': '{"icon": "mdi:attachment", "title": "attachment.category.category", "menuVisibleWithForbidden": "false"}', 'permission': '{"add": true, "edit": true, "view": true, "delete": true}', 'menu_display_type': 'ajax', 'model_name': 'attachmentCategory', 'deleted_at': None, 'weigh': 0, 'status': 'normal', 'created_at': datetime.fromisoformat('2025-03-06T03:54:07'), 'updated_at': datetime.fromisoformat('2025-03-06T12:56:31') },
        { 'id': 25, 'rule_type': 'menu', 'parent_id': 9, 'name': 'plugin', 'path': '/plugin/plugin', 'component': '/_core/plugin/plugin', 'redirect': '', 'meta': '{"icon": "mdi:shape-rectangle-add", "title": "plugin.plugin", "menuVisibleWithForbidden": "false"}', 'permission': '{"add": true, "edit": true, "view": true, "delete": true}', 'menu_display_type': 'ajax', 'model_name': 'plugin', 'deleted_at': None, 'weigh': 0, 'status': 'normal', 'created_at': datetime.fromisoformat('2025-03-09T02:40:04'), 'updated_at': datetime.fromisoformat('2025-03-09T11:05:32') },
        { 'id': 26, 'rule_type': 'menu', 'parent_id': 9, 'name': 'plugin_store', 'path': '/plugin/plugin_store', 'component': '/_core/plugin_store', 'redirect': '', 'meta': '{"icon": "mdi:all-inclusive", "title": "plugin.plugin_store", "menuVisibleWithForbidden": "false"}', 'permission': '{"enable": true, "disable": true, "install": true, "unstall": true}', 'menu_display_type': 'ajax', 'model_name': 'online_plugin', 'deleted_at': None, 'weigh': 0, 'status': 'normal', 'created_at': datetime.fromisoformat('2025-03-10T07:15:54'), 'updated_at': datetime.fromisoformat('2025-03-10T16:07:41') },
        { 'id': 27, 'rule_type': 'menu', 'parent_id': 1, 'name': 'analytics', 'path': '/dashboard/analytics', 'component': '/_core/dashboard/analytics/index', 'redirect': None, 'meta': '{"icon": "mdi:view-dashboard-outline", "title": "dashboard.analytics"}', 'permission': '{"view": true}', 'menu_display_type': 'addtabs', 'model_name': 'Dashboard', 'deleted_at': None, 'weigh': 1, 'status': 'normal', 'created_at': datetime.fromisoformat('2024-01-22T14:32:00'), 'updated_at': datetime.fromisoformat('2025-03-04T07:36:31') },
    ])

    table_sys_user_rule = sa.table(
        'sys_user_rule',
        sa.column('id', sa.Integer),
        sa.column('rule_type', sa.Enum),
        sa.column('parent_id', sa.Integer),
        sa.column('name', sa.String),
        sa.column('path', sa.String),
        sa.column('component', sa.String),
        sa.column('redirect', sa.String),
        sa.column('meta', sa.JSON),
        sa.column('permission', sa.JSON),
        sa.column('menu_display_type', sa.Enum),
        sa.column('model_name', sa.String),
        sa.column('deleted_at', sa.DATETIME),
        sa.column('weigh', sa.Integer),
        sa.column('status', sa.Enum),
        sa.column('created_at', sa.DateTime),
        sa.column('updated_at', sa.DateTime),
    )
    op.bulk_insert(table_sys_user_rule, [
        { 'id': 1, 'rule_type': 'menu', 'parent_id': 0, 'name': 'userHome', 'path': '/home', 'component': '/user/home', 'redirect': '/dashboard', 'meta': '{"icon": "mdi:home", "title": "home.home"}', 'permission': '{}', 'menu_display_type': 'addtabs', 'model_name': 'Home', 'deleted_at': None, 'weigh': 1, 'status': 'normal', 'created_at': datetime.fromisoformat('2024-01-22T14:32:00'), 'updated_at': datetime.fromisoformat('2025-07-01T09:21:36') },
        { 'id': 2, 'rule_type': 'menu', 'parent_id': 0, 'name': 'userProfile', 'path': '/profile', 'component': '/user/profile', 'redirect': None, 'meta': '{"icon": "mdi:account", "title": "profile.profile"}', 'permission': '{}', 'menu_display_type': 'addtabs', 'model_name': 'Profile', 'deleted_at': None, 'weigh': 1, 'status': 'normal', 'created_at': datetime.fromisoformat('2024-01-22T14:32:00'), 'updated_at': datetime.fromisoformat('2025-07-01T09:22:00') },
        { 'id': 3, 'rule_type': 'menu', 'parent_id': 0, 'name': 'userSetting', 'path': '/setting', 'component': '/user/setting', 'redirect': None, 'meta': '{"icon": "mdi:cog", "title": "setting.setting"}', 'permission': '{}', 'menu_display_type': 'addtabs', 'model_name': 'Setting', 'deleted_at': None, 'weigh': 2, 'status': 'normal', 'created_at': datetime.fromisoformat('2024-01-22T14:32:00'), 'updated_at': datetime.fromisoformat('2025-07-01T09:21:36') },
    ])

    table_sys_admin_group = sa.table(
        'sys_admin_group',
        sa.column('id', sa.Integer),
        sa.column('pid', sa.Integer),
        sa.column('name', sa.String),
        sa.column('rules', sa.JSON),
        sa.column('access', sa.JSON),
        sa.column('status', sa.Enum),
        sa.column('created_at', sa.DateTime),
        sa.column('updated_at', sa.DateTime),
    )
    op.bulk_insert(table_sys_admin_group, [
        { 'id': 1, 'pid': 0, 'name': 'super', 'rules': ['all'], 'access': ['all'], 'status': 'normal', 'created_at': datetime.fromisoformat('2024-04-05T12:15:11'), 'updated_at': datetime.fromisoformat('2025-03-04T15:54:49') },
    ])

    table_sys_plugin = sa.table(
        'sys_plugin',
        sa.column('id', sa.Integer),
        sa.column('title', sa.String),
        sa.column('author', sa.String),
        sa.column('uuid', sa.String),
        sa.column('description', sa.String),
        sa.column('version', sa.String),
        sa.column('downloads', sa.Integer),
        sa.column('download_url', sa.String),
        sa.column('md5_hash', sa.String),
        sa.column('price', sa.DECIMAL),
        sa.column('paid', sa.SMALLINT),
        sa.column('installed', sa.SMALLINT),
        sa.column('enabled', sa.SMALLINT),
        sa.column('setting_menu', sa.String),
        sa.column('status', sa.Enum),
        sa.column('created_at', sa.DateTime),
        sa.column('updated_at', sa.DateTime),
    )
    op.bulk_insert(table_sys_plugin, [
        { 'id': 1, 'title': '代码生成器', 'author': 'StkFish', 'uuid': 'generator', 'description': 'generator', 'version': '1.0.1', 'downloads': 12, 'download_url': '2', 'md5_hash': '2', 'price': Decimal('10'), 'paid': 0, 'installed': 1, 'enabled': 1, 'setting_menu': '0', 'status': 'normal', 'created_at': datetime.fromisoformat('2025-03-10T17:09:22'), 'updated_at': datetime.fromisoformat('2025-05-09T09:34:40') },
    ])

    table_sys_attachment_category = sa.table(
        'sys_attachment_category',
        sa.column('id', sa.Integer),
        sa.column('pid', sa.Integer),
        sa.column('name', sa.String),
        sa.column('status', sa.Enum),
        sa.column('created_at', sa.DateTime),
        sa.column('updated_at', sa.DateTime),
    )
    op.bulk_insert(table_sys_attachment_category, [
        { 'id': 1, 'pid': 0, 'name': 'default', 'status': 'normal', 'created_at': datetime.fromisoformat('2025-03-06T12:00:02'), 'updated_at': datetime.fromisoformat('2025-03-07T09:10:48') },
    ])

    table_sys_user_group = sa.table(
        'sys_user_group',
        sa.column('id', sa.Integer),
        sa.column('pid', sa.Integer),
        sa.column('name', sa.String),
        sa.column('rules', sa.JSON),
        sa.column('access', sa.JSON),
        sa.column('status', sa.Enum),
        sa.column('created_at', sa.DateTime),
        sa.column('updated_at', sa.DateTime),
    )
    op.bulk_insert(table_sys_user_group, [
        { 'id': 1, 'pid': 0, 'name': 'super', 'rules': '{"permissions": ["all"]}', 'access': '{"permissions": ["all"]}', 'status': 'normal', 'created_at': datetime.fromisoformat('2024-04-05T12:15:11'), 'updated_at': datetime.fromisoformat('2025-11-19T09:29:53') },
    ])

    table_sys_general_config = sa.table(
        'sys_general_config',
        sa.column('id', sa.Integer),
        sa.column('name', sa.String),
        sa.column('group', sa.String),
        sa.column('title', sa.String),
        sa.column('tip', sa.String),
        sa.column('type', sa.String),
        sa.column('visible', sa.String),
        sa.column('value', sa.TEXT),
        sa.column('content', sa.TEXT),
        sa.column('rule', sa.String),
        sa.column('extend', sa.String),
        sa.column('setting', sa.String),
        sa.column('created_at', sa.DateTime),
        sa.column('updated_at', sa.DateTime),
    )
    op.bulk_insert(table_sys_general_config, [
        { 'id': 1, 'name': 'name', 'group': 'basic', 'title': 'Site name', 'tip': 'Please Input  Site name', 'type': 'string', 'visible': '', 'value': '栈鱼后台管理系统Pro 1.0', 'content': '', 'rule': 'required', 'extend': '', 'setting': '', 'created_at': datetime.fromisoformat('2024-12-29T01:39:29'), 'updated_at': datetime.fromisoformat('2024-12-27T11:57:06') },
        { 'id': 2, 'name': 'copyright', 'group': 'basic', 'title': 'Copyright', 'tip': 'Please Input  Copyright', 'type': 'string', 'visible': '', 'value': 'Copyright © 2024 <a href="https://zayum.com" class="text-subtitle-2">栈鱼后台管理系统 1.0</a>. All rights reserved.', 'content': '', 'rule': '', 'extend': '', 'setting': '', 'created_at': datetime.fromisoformat('2024-12-29T01:39:29'), 'updated_at': datetime.fromisoformat('2024-12-27T11:57:06') },
        { 'id': 3, 'name': 'cdnurl', 'group': 'basic', 'title': 'Cdn url', 'tip': 'Please Input  Site name', 'type': 'string', 'visible': '', 'value': 'https://zhanor.com', 'content': '', 'rule': '', 'extend': '', 'setting': '', 'created_at': datetime.fromisoformat('2024-12-29T01:39:29'), 'updated_at': datetime.fromisoformat('2024-12-27T11:57:06') },
        { 'id': 4, 'name': 'version', 'group': 'basic', 'title': 'Version', 'tip': 'Please Input  Version', 'type': 'string', 'visible': '', 'value': '1.0.1', 'content': '', 'rule': 'required', 'extend': '', 'setting': '', 'created_at': datetime.fromisoformat('2024-12-29T01:39:29'), 'updated_at': datetime.fromisoformat('2024-12-27T11:57:06') },
        { 'id': 5, 'name': 'timezone', 'group': 'basic', 'title': 'Timezone', 'tip': '', 'type': 'string', 'visible': '', 'value': 'Asia/Shanghai', 'content': '', 'rule': 'required', 'extend': '', 'setting': '', 'created_at': datetime.fromisoformat('2024-12-29T01:39:29'), 'updated_at': datetime.fromisoformat('2024-12-27T11:57:06') },
        { 'id': 6, 'name': 'forbiddenip', 'group': 'basic', 'title': 'Forbidden ip', 'tip': 'Please Input  Forbidden ip', 'type': 'text', 'visible': '', 'value': '12.23.21.1\n1.2.3.6\n34.78.43.1', 'content': '', 'rule': '', 'extend': '', 'setting': '', 'created_at': datetime.fromisoformat('2025-04-29T07:12:13'), 'updated_at': datetime.fromisoformat('2025-04-29T07:12:13') },
        { 'id': 7, 'name': 'languages', 'group': 'basic', 'title': 'Languages', 'tip': '', 'type': 'array', 'visible': '', 'value': '{"frontend": "zh-cn", "backend": "zh-cn"}', 'content': '', 'rule': 'required', 'extend': '', 'setting': '', 'created_at': datetime.fromisoformat('2024-12-29T01:39:29'), 'updated_at': datetime.fromisoformat('2024-12-29T01:39:29') },
        { 'id': 8, 'name': 'fixedpage', 'group': 'basic', 'title': 'Fixed page', 'tip': 'Please Input Fixed page', 'type': 'string', 'visible': '', 'value': 'dashboard', 'content': '', 'rule': 'required', 'extend': '', 'setting': '', 'created_at': datetime.fromisoformat('2024-12-29T01:39:29'), 'updated_at': datetime.fromisoformat('2024-12-27T11:57:06') },
        { 'id': 9, 'name': 'categorytype', 'group': 'dictionary', 'title': 'Category type', 'tip': '', 'type': 'array', 'visible': '', 'value': '{"default": "Default", "page": "Page", "article": "Article"}', 'content': '', 'rule': '', 'extend': '', 'setting': '', 'created_at': datetime.fromisoformat('2024-12-29T01:39:29'), 'updated_at': datetime.fromisoformat('2024-12-27T11:57:06') },
        { 'id': 10, 'name': 'default_category', 'group': 'dictionary', 'title': 'Default Category', 'tip': '', 'type': 'array', 'visible': '', 'value': '{"default": "Default"}', 'content': '', 'rule': '', 'extend': '', 'setting': '', 'created_at': datetime.fromisoformat('2024-12-29T01:39:29'), 'updated_at': datetime.fromisoformat('2024-12-27T11:57:06') },
        { 'id': 11, 'name': 'mail_type', 'group': 'email', 'title': 'Mail type', 'tip': 'Please Input Mail type', 'type': 'select', 'visible': '', 'value': 'SMTP', 'content': '["Please Select","SMTP"]', 'rule': '', 'extend': '', 'setting': '', 'created_at': datetime.fromisoformat('2024-12-29T01:39:29'), 'updated_at': datetime.fromisoformat('2024-12-29T20:59:28') },
        { 'id': 12, 'name': 'mail_smtp_host', 'group': 'email', 'title': 'Mail smtp host', 'tip': 'Please Input Mail smtp host', 'type': 'string', 'visible': '', 'value': 'smtp.qq.com', 'content': '', 'rule': '', 'extend': '', 'setting': '', 'created_at': datetime.fromisoformat('2024-12-29T01:39:29'), 'updated_at': datetime.fromisoformat('2024-12-27T11:57:06') },
        { 'id': 13, 'name': 'mail_smtp_port', 'group': 'email', 'title': 'Mail smtp port', 'tip': 'Please Input  Mail smtp port(default25,SSL：465,TLS：587)', 'type': 'string', 'visible': '', 'value': '465', 'content': '', 'rule': '', 'extend': '', 'setting': '', 'created_at': datetime.fromisoformat('2024-12-29T01:39:29'), 'updated_at': datetime.fromisoformat('2024-12-27T11:57:06') },
        { 'id': 14, 'name': 'mail_smtp_user', 'group': 'email', 'title': 'Mail smtp user', 'tip': 'Please Input Mail smtp user', 'type': 'string', 'visible': '', 'value': '10000', 'content': '', 'rule': '', 'extend': '', 'setting': '', 'created_at': datetime.fromisoformat('2024-12-29T01:39:29'), 'updated_at': datetime.fromisoformat('2024-12-27T11:57:06') },
        { 'id': 15, 'name': 'mail_smtp_pass', 'group': 'email', 'title': 'Mail smtp password', 'tip': 'Please Input  Mail smtp password', 'type': 'string', 'visible': '', 'value': 'password', 'content': '', 'rule': '', 'extend': '', 'setting': '', 'created_at': datetime.fromisoformat('2024-12-29T01:39:29'), 'updated_at': datetime.fromisoformat('2024-12-27T11:57:06') },
        { 'id': 16, 'name': 'mail_verify_type', 'group': 'email', 'title': 'Mail vertify type', 'tip': 'Please Input Mail vertify type', 'type': 'select', 'visible': '', 'value': 'TLS', 'content': '["None","TLS","SSL"]', 'rule': '', 'extend': '', 'setting': '', 'created_at': datetime.fromisoformat('2024-12-29T01:39:29'), 'updated_at': datetime.fromisoformat('2024-12-29T20:58:05') },
        { 'id': 17, 'name': 'mail_from', 'group': 'email', 'title': 'Mail from', 'tip': '', 'type': 'string', 'visible': '', 'value': '10000@qq.com', 'content': '', 'rule': '', 'extend': '', 'setting': '', 'created_at': datetime.fromisoformat('2024-12-29T01:39:29'), 'updated_at': datetime.fromisoformat('2024-12-27T11:57:06') },
        { 'id': 18, 'name': 'image_category', 'group': 'dictionary', 'title': 'Attachment Image category', 'tip': '', 'type': 'array', 'visible': '', 'value': '{"default": "Default", "blog": "Blog"}', 'content': '', 'rule': '', 'extend': '', 'setting': '', 'created_at': datetime.fromisoformat('2024-12-29T01:39:29'), 'updated_at': datetime.fromisoformat('2024-12-29T01:39:29') },
        { 'id': 19, 'name': 'file_category', 'group': 'dictionary', 'title': 'Attachment File category', 'tip': '', 'type': 'array', 'visible': '', 'value': '{"default": "Default", "product": "Product"}', 'content': '', 'rule': '', 'extend': '', 'setting': '', 'created_at': datetime.fromisoformat('2024-12-29T01:39:29'), 'updated_at': datetime.fromisoformat('2024-12-29T01:39:29') },
        { 'id': 20, 'name': 'video_category', 'group': 'dictionary', 'title': 'Attachment Video category', 'tip': '', 'type': 'array', 'visible': '', 'value': '{"default": "Default", "tutorial": "Tutorial"}', 'content': '', 'rule': '', 'extend': '', 'setting': '', 'created_at': datetime.fromisoformat('2024-12-29T01:39:29'), 'updated_at': datetime.fromisoformat('2024-12-29T01:39:29') },
        { 'id': 21, 'name': 'audio_category', 'group': 'dictionary', 'title': 'Attachment Audio category', 'tip': '', 'type': 'array', 'visible': '', 'value': '{"default": "Default", "music": "Music"}', 'content': '', 'rule': '', 'extend': '', 'setting': '', 'created_at': datetime.fromisoformat('2024-12-29T01:39:29'), 'updated_at': datetime.fromisoformat('2024-12-29T01:39:29') },
        { 'id': 22, 'name': 'document_category', 'group': 'dictionary', 'title': 'Attachment Document category', 'tip': '', 'type': 'array', 'visible': '', 'value': '{"default": "Default", "contract": "Contract"}', 'content': '', 'rule': '', 'extend': '', 'setting': '', 'created_at': datetime.fromisoformat('2024-12-29T01:39:29'), 'updated_at': datetime.fromisoformat('2024-12-29T01:39:29') },
        { 'id': 23, 'name': 'user_page_title', 'group': 'user', 'title': 'User Page Title', 'tip': 'User Page Title', 'type': 'string', 'visible': '', 'value': 'User Center', 'content': '', 'rule': 'letters', 'extend': '', 'setting': '', 'created_at': datetime.fromisoformat('2024-12-29T01:39:29'), 'updated_at': datetime.fromisoformat('2024-12-30T12:50:59') },
        { 'id': 24, 'name': 'user_footer', 'group': 'user', 'title': 'User Center Footer', 'tip': 'User Center Footer', 'type': 'text', 'visible': '', 'value': 'Copyright © 2024 <a href="https://zayum.com" class="link-secondary">会员中心</a>. All rights reserved.', 'content': '', 'rule': 'required', 'extend': '', 'setting': '', 'created_at': datetime.fromisoformat('2024-12-29T01:39:29'), 'updated_at': datetime.fromisoformat('2024-12-30T12:50:59') },
    ])


def downgrade():
    op.execute("DELETE FROM sys_admin WHERE id IN (1)")

    op.execute("DELETE FROM sys_general_category WHERE id IN (1,2)")

    op.execute("DELETE FROM sys_admin_rule WHERE id IN (1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,22,24,25,26,27)")

    op.execute("DELETE FROM sys_user_rule WHERE id IN (1,2,3)")

    op.execute("DELETE FROM sys_admin_group WHERE id IN (1)")

    op.execute("DELETE FROM sys_plugin WHERE id IN (1)")

    op.execute("DELETE FROM sys_attachment_category WHERE id IN (1)")

    op.execute("DELETE FROM sys_user_group WHERE id IN (1)")

    op.execute("DELETE FROM sys_general_config WHERE id IN (1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24)")
