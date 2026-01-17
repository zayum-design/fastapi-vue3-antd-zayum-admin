"""导入模型数据脚本，不依赖 Alembic"""
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy.orm import Session
from app.dependencies.database import SessionLocal
from app.models import *

def import_data():
    db = SessionLocal()
    try:
        # 插入 sys_admin 表数据
        sys_admin = SysAdmin()
        sys_admin.id = 1
        sys_admin.group_id = 1
        sys_admin.username = 'admin'
        sys_admin.nickname = 'SupperAdmin'
        sys_admin.password = '$2b$12$PSRSTAdY7Vi8bFgeD5BOA.ZDozJ9rPYVklWGC6y6o7om6QWgR.WlW'
        sys_admin.avatar = '/uploads/avatar/avatar_1_c7b7e5.png'
        sys_admin.email = '13800000000@qq.com'
        sys_admin.mobile = '13800000000'
        sys_admin.login_failure = 0
        sys_admin.login_at = datetime.fromisoformat('2025-11-29T01:53:50')
        sys_admin.login_ip = '127.0.0.1'
        sys_admin.token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzY0OTg2MDMwfQ.RE7NJAattKcfoRKYRMUIByfllR85Dj7iXYV5j76L49U'
        sys_admin.status = 'normal'
        sys_admin.created_at = datetime.fromisoformat('2025-06-26T02:59:10')
        sys_admin.updated_at = datetime.fromisoformat('2025-11-29T01:53:50')
        db.add(sys_admin)

        # 插入 sys_general_category 表数据
        sys_general_category = SysGeneralCategory()
        sys_general_category.id = 1
        sys_general_category.pid = 0
        sys_general_category.type = 'default'
        sys_general_category.name = 'default'
        sys_general_category.thumb = ''
        sys_general_category.keywords = ''
        sys_general_category.description = ''
        sys_general_category.weigh = 0
        sys_general_category.status = 'normal'
        sys_general_category.created_at = datetime.fromisoformat('2024-05-08T17:19:06')
        sys_general_category.updated_at = datetime.fromisoformat('2025-03-07T11:50:19')
        db.add(sys_general_category)
        sys_general_category = SysGeneralCategory()
        sys_general_category.id = 2
        sys_general_category.pid = 0
        sys_general_category.type = 'blog'
        sys_general_category.name = 'news'
        sys_general_category.thumb = ''
        sys_general_category.keywords = ''
        sys_general_category.description = ''
        sys_general_category.weigh = 0
        sys_general_category.status = 'normal'
        sys_general_category.created_at = datetime.fromisoformat('2025-06-04T17:47:14')
        sys_general_category.updated_at = datetime.fromisoformat('2025-06-04T17:47:14')
        db.add(sys_general_category)

        # 插入 sys_admin_rule 表数据
        sys_admin_rule_data = [
            (1, 'menu', 0, 'dashboard', '/dashboard/', '/_core/dashboard/dashboard', '/dashboard', {'icon': 'mdi:view-dashboard-outline', 'title': 'dashboard.dashboard'}, {}, 'addtabs', 'Dashboard', None, 1, 'normal', datetime.fromisoformat('2024-01-22T14:32:00'), datetime.fromisoformat('2025-11-11T01:23:42')),
            (2, 'menu', 1, 'workspace', '/dashboard/workspace', '/_core/dashboard/workspace/index', None, {'icon': 'mdi:view-dashboard-outline', 'title': 'dashboard.workspace.workspace'}, {'view': True}, 'addtabs', 'Dashboard', None, 1, 'normal', datetime.fromisoformat('2024-01-22T14:32:00'), datetime.fromisoformat('2025-06-05T00:22:17')),
            (3, 'menu', 0, 'generals', '/generals', None, None, {'icon': 'mdi:cog-outline', 'title': 'general.general'}, '{}', 'addtabs', 'Generals', None, 2, 'normal', datetime.fromisoformat('2024-01-22T14:32:00'), datetime.fromisoformat('2025-02-28T18:40:34')),
            (4, 'menu', 3, 'general.profile', '/general/profile', '/_core/general/profile', None, {'icon': 'mdi:account-outline', 'title': 'general.profile.profile'}, {'edit': True}, 'addtabs', 'GeneralProfile', None, 11, 'normal', datetime.fromisoformat('2024-01-22T14:32:00'), datetime.fromisoformat('2025-02-28T12:04:00')),
            (5, 'menu', 3, 'general.category', '/general/category', '/_core/general/category', '', {'icon': 'mdi:category-plus-outline', 'title': 'general.category.category', 'menuVisibleWithForbidden': 'false'}, {'add': True, 'edit': True, 'view': True, 'delete': True}, 'ajax', 'GeneralsCategory', None, 0, 'normal', datetime.fromisoformat('2025-03-04T03:24:40'), datetime.fromisoformat('2025-03-07T11:12:12')),
            (6, 'menu', 3, 'general.config', '/general/config', '/_core/general/config', None, {'icon': 'mdi:cog-outline', 'title': 'general.config.config'}, {'add': True, 'edit': True, 'delete': True}, 'addtabs', 'GeneralConfig', None, 8, 'normal', datetime.fromisoformat('2024-01-22T14:32:00'), datetime.fromisoformat('2025-03-04T07:36:31')),
            (7, 'menu', 0, 'attachments', '/attachments', None, None, {'icon': 'mdi:paperclip', 'title': 'attachment.attachment_manage'}, '{}', 'blank', 'Attachment', None, 9, 'normal', datetime.fromisoformat('2024-01-22T14:32:00'), datetime.fromisoformat('2025-03-06T11:39:00')),
            (8, 'menu', 7, 'attachment.attachment', '/attachment/attachment', '/_core/attachment/attachment', None, {'icon': 'mdi:file-outline', 'title': 'attachment.attachment'}, {'add': True, 'edit': True, 'view': True, 'delete': True}, 'addtabs', 'Attachment', None, 10, 'normal', datetime.fromisoformat('2024-01-22T14:32:00'), datetime.fromisoformat('2025-03-06T11:39:00')),
            (9, 'menu', 0, 'plugins', '/plugins', None, None, {'icon': 'mdi:puzzle-outline', 'title': 'plugin.plugin', 'childComponent': '/_core/general/profile'}, '{}', 'addtabs', 'Plugin', None, 3, 'normal', datetime.fromisoformat('2024-01-22T14:32:00'), datetime.fromisoformat('2025-02-28T17:51:12')),
            (10, 'menu', 0, 'admin', '/admin', None, None, {'icon': 'mdi:shield-account-outline', 'title': 'admin.admin.field.admin'}, '{}', 'addtabs', 'Admin', None, 4, 'normal', datetime.fromisoformat('2024-01-22T14:32:00'), datetime.fromisoformat('2025-06-04T12:15:36')),
            (11, 'menu', 10, 'admin.admin', '/admin/admin', '/_core/admin/admin', None, {'icon': 'mdi:account-outline', 'title': 'admin.admin.admin_manage'}, {'add': True, 'ajax': True, 'edit': True, 'view': True, 'delete': True}, 'addtabs', 'Admin', None, 20, 'normal', datetime.fromisoformat('2024-01-22T14:32:00'), datetime.fromisoformat('2025-03-06T16:24:24')),
            (12, 'menu', 10, 'admin.group', '/admin/group', '/_core/admin/group', None, {'icon': 'mdi:account-group-outline', 'title': 'admin.group.group'}, {'add': True, 'ajax': True, 'edit': True, 'view': True, 'delete': True}, 'addtabs', 'AdminGroup', None, 21, 'normal', datetime.fromisoformat('2024-01-22T14:32:00'), datetime.fromisoformat('2025-03-06T13:03:05')),
            (13, 'menu', 10, 'admin.rule', '/admin/rule', '/_core/admin/rule', None, {'icon': 'mdi:shield-account-outline', 'title': 'admin.rule.rule'}, {'add': True, 'edit': True, 'view': True, 'delete': True}, 'addtabs', 'AdminRule', None, 47, 'normal', datetime.fromisoformat('2024-01-22T14:32:00'), datetime.fromisoformat('2025-03-06T13:03:05')),
            (14, 'menu', 10, 'admin.log', '/admin/log', '/_core/admin/log', None, {'icon': 'mdi:clipboard-text-outline', 'title': 'admin.log.log'}, {'view': True}, 'addtabs', 'AdminLog', None, 50, 'normal', datetime.fromisoformat('2024-01-22T14:32:00'), datetime.fromisoformat('2025-03-04T07:36:31')),
            (15, 'menu', 0, 'users', '/users', None, None, {'icon': 'mdi:account-multiple-outline', 'title': 'user.user'}, '{}', 'addtabs', 'Users', None, 24, 'normal', datetime.fromisoformat('2024-01-22T14:32:00'), datetime.fromisoformat('2025-02-26T17:47:48')),
            (16, 'menu', 15, 'user', '/user', '/_core/user/user', None, {'icon': 'mdi:account-outline', 'title': 'user.user_manage'}, {'add': True, 'edit': True, 'view': True, 'delete': True}, 'addtabs', 'User', None, 24, 'normal', datetime.fromisoformat('2024-01-22T14:32:00'), datetime.fromisoformat('2025-03-06T16:19:59')),
            (17, 'menu', 15, 'user.rule', '/user/rule', '/_core/user/rule', None, {'icon': 'mdi:shield-account-outline', 'title': 'user.rule.rule'}, {'add': True, 'edit': True, 'view': True, 'delete': True}, 'addtabs', 'UserRule', None, 26, 'normal', datetime.fromisoformat('2024-01-22T14:32:00'), datetime.fromisoformat('2025-03-04T07:36:31')),
            (18, 'menu', 15, 'user.balance.log', '/user/balance/log', '/_core/user/balance_log', None, {'icon': 'mdi:account-balance-wallet-outline', 'title': 'user.balance_log.balance_log'}, {'add': True, 'edit': True, 'view': True, 'delete': True}, 'addtabs', 'UserBalance', None, 25, 'normal', datetime.fromisoformat('2024-01-22T14:32:00'), datetime.fromisoformat('2025-03-06T16:27:28')),
            (19, 'menu', 15, 'user.score.log', '/user/score/log', '/_core/user/score_log', None, {'icon': 'mdi:scoreboard-outline', 'title': 'user.score_log.score_log'}, {'add': True, 'edit': True, 'view': True, 'delete': True}, 'addtabs', 'UserScore', None, 25, 'normal', datetime.fromisoformat('2024-01-22T14:32:00'), datetime.fromisoformat('2025-03-06T16:28:37')),
            (20, 'menu', 15, 'user.group', '/user/group', '/_core/user/group', None, {'icon': 'mdi:account-group-outline', 'title': 'user.group.group'}, {'add': True, 'edit': True, 'view': True, 'delete': True}, 'addtabs', 'UserGroup', None, 0, 'normal', datetime.fromisoformat('2024-09-26T13:01:14'), datetime.fromisoformat('2025-03-04T07:36:31')),
            (22, 'menu', 9, 'generator', '/plugins/generator', '/plugins/generator', '', {'icon': 'mdi:codepen', 'title': 'generator.code_generator', 'menuVisibleWithForbidden': 'false'}, {'view': True}, 'ajax', 'generator', None, 0, 'normal', datetime.fromisoformat('2025-02-28T10:31:33'), datetime.fromisoformat('2025-03-04T07:36:31')),
            (24, 'menu', 7, 'attachmentCategory', '/attachment/category', '/_core/attachment/category', '', {'icon': 'mdi:attachment', 'title': 'attachment.category.category', 'menuVisibleWithForbidden': 'false'}, {'add': True, 'edit': True, 'view': True, 'delete': True}, 'ajax', 'attachmentCategory', None, 0, 'normal', datetime.fromisoformat('2025-03-06T03:54:07'), datetime.fromisoformat('2025-03-06T12:56:31')),
            (25, 'menu', 9, 'plugin', '/plugin/plugin', '/_core/plugin/plugin', '', {'icon': 'mdi:shape-rectangle-add', 'title': 'plugin.plugin', 'menuVisibleWithForbidden': 'false'}, {'add': True, 'edit': True, 'view': True, 'delete': True}, 'ajax', 'plugin', None, 0, 'normal', datetime.fromisoformat('2025-03-09T02:40:04'), datetime.fromisoformat('2025-03-09T11:05:32')),
            (26, 'menu', 9, 'plugin_store', '/plugin/plugin_store', '/_core/plugin_store', '', {'icon': 'mdi:all-inclusive', 'title': 'plugin.plugin_store', 'menuVisibleWithForbidden': 'false'}, {'enable': True, 'disable': True, 'install': True, 'unstall': True}, 'ajax', 'online_plugin', None, 0, 'normal', datetime.fromisoformat('2025-03-10T07:15:54'), datetime.fromisoformat('2025-03-10T16:07:41')),
            (27, 'menu', 1, 'analytics', '/dashboard/analytics', '/_core/dashboard/analytics/index', None, {'icon': 'mdi:view-dashboard-outline', 'title': 'dashboard.analytics'}, {'view': True}, 'addtabs', 'Dashboard', None, 1, 'normal', datetime.fromisoformat('2024-01-22T14:32:00'), datetime.fromisoformat('2025-03-04T07:36:31')),
        ]

        for sys_admin_rule_item in sys_admin_rule_data:
            item = SysAdminRule()
            item.id = sys_admin_rule_item[0]
            item.rule_type = sys_admin_rule_item[1]
            item.parent_id = sys_admin_rule_item[2]
            item.name = sys_admin_rule_item[3]
            item.path = sys_admin_rule_item[4]
            item.component = sys_admin_rule_item[5]
            item.redirect = sys_admin_rule_item[6]
            item.meta = sys_admin_rule_item[7]
            item.permission = sys_admin_rule_item[8]
            item.menu_display_type = sys_admin_rule_item[9]
            item.model_name = sys_admin_rule_item[10]
            item.deleted_at = sys_admin_rule_item[11]
            item.weigh = sys_admin_rule_item[12]
            item.status = sys_admin_rule_item[13]
            item.created_at = sys_admin_rule_item[14]
            item.updated_at = sys_admin_rule_item[15]
            db.add(item)

        # 插入 sys_admin_log 表数据
        sys_admin_log = SysAdminLog()
        sys_admin_log.id = 1
        sys_admin_log.admin_id = 1
        sys_admin_log.username = 'admin'
        sys_admin_log.url = 'http://127.0.0.1:8000/api/admin/user/create'
        sys_admin_log.title = 'POST'
        sys_admin_log.content = '{"user_group_id": 1, "username": "uuuu", "nickname": "uuuu", "password": "*", "email": "dsfa@ddd.ccc", "mobile": "13345443233", "avatar": "", "level": 0, "gender": "male", "birthday": "2025-11-27", "bio": "", "balance": 0, "score": 0, "successions": 0, "max_successions": 0, "prev_time": "2025-11-27 11:58:30", "login_time": "2025-11-27 11:58:30", "login_ip": "", "login_failure": 0, "join_ip": "", "verification": "", "token": "", "status": "normal", "platform": "web", "created_at": "2025-11-27 11:58:30", "updated_at": "2025-11-27 11:58:30"}'
        sys_admin_log.ip = '127.0.0.1'
        sys_admin_log.useragent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36'
        sys_admin_log.created_at = datetime.fromisoformat('2025-11-27T03:59:30')
        sys_admin_log.updated_at = datetime.fromisoformat('2025-11-27T03:59:30')
        db.add(sys_admin_log)
        sys_admin_log = SysAdminLog()
        sys_admin_log.id = 2
        sys_admin_log.admin_id = 1
        sys_admin_log.username = 'admin'
        sys_admin_log.url = 'http://127.0.0.1:8000/api/admin/admin/update/1'
        sys_admin_log.title = 'PUT'
        sys_admin_log.content = '{"id": 1, "group_id": 1, "username": "admin", "nickname": "SupperAdmin", "avatar": "/uploads/avatar/avatar_1_c7b7e5.png", "email": "13800000000@qq.com", "mobile": "13800000000", "login_failure": 0, "login_at": "2025-11-29 01:26:27", "login_ip": "127.0.0.1", "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzY0OTg0Mzg3fQ.6kogc16gtD9ipLIr7eqrwgBCRQvtSdkBTx5VvFJF6oQ", "status": "normal", "created_at": "2025-06-26 02:59:10", "updated_at": "2025-11-29 01:26:27", "password": "*"}'
        sys_admin_log.ip = '127.0.0.1'
        sys_admin_log.useragent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36'
        sys_admin_log.created_at = datetime.fromisoformat('2025-11-29T01:53:39')
        sys_admin_log.updated_at = datetime.fromisoformat('2025-11-29T01:53:39')
        db.add(sys_admin_log)

        # 插入 sys_user_rule 表数据
        sys_user_rule_data = [
            (1, 'menu', 0, 'userHome', '/home', '/user/home', '/dashboard', {'icon': 'mdi:home', 'title': 'home.home'}, {}, 'addtabs', 'Home', None, 1, 'normal', datetime.fromisoformat('2024-01-22T14:32:00'), datetime.fromisoformat('2025-07-01T09:21:36')),
            (2, 'menu', 0, 'userProfile', '/profile', '/user/profile', None, {'icon': 'mdi:account', 'title': 'profile.profile'}, {}, 'addtabs', 'Profile', None, 1, 'normal', datetime.fromisoformat('2024-01-22T14:32:00'), datetime.fromisoformat('2025-07-01T09:22:00')),
            (3, 'menu', 0, 'userSetting', '/setting', '/user/setting', None, {'icon': 'mdi:cog', 'title': 'setting.setting'}, {}, 'addtabs', 'Setting', None, 2, 'normal', datetime.fromisoformat('2024-01-22T14:32:00'), datetime.fromisoformat('2025-07-01T09:21:36')),
        ]

        for sys_user_rule_item in sys_user_rule_data:
            item = SysUserRule()
            item.id = sys_user_rule_item[0]
            item.rule_type = sys_user_rule_item[1]
            item.parent_id = sys_user_rule_item[2]
            item.name = sys_user_rule_item[3]
            item.path = sys_user_rule_item[4]
            item.component = sys_user_rule_item[5]
            item.redirect = sys_user_rule_item[6]
            item.meta = sys_user_rule_item[7]
            item.permission = sys_user_rule_item[8]
            item.menu_display_type = sys_user_rule_item[9]
            item.model_name = sys_user_rule_item[10]
            item.deleted_at = sys_user_rule_item[11]
            item.weigh = sys_user_rule_item[12]
            item.status = sys_user_rule_item[13]
            item.created_at = sys_user_rule_item[14]
            item.updated_at = sys_user_rule_item[15]
            db.add(item)

        # 插入 sys_admin_group 表数据
        sys_admin_group = SysAdminGroup()
        sys_admin_group.id = 1
        sys_admin_group.pid = 0
        sys_admin_group.name = 'super'
        sys_admin_group.rules = ['all']
        sys_admin_group.access = ['all']
        sys_admin_group.status = 'normal'
        sys_admin_group.created_at = datetime.fromisoformat('2024-04-05T12:15:11')
        sys_admin_group.updated_at = datetime.fromisoformat('2025-03-04T15:54:49')
        db.add(sys_admin_group)

        # 插入 sys_plugin 表数据
        sys_plugin = SysPlugin()
        sys_plugin.id = 1
        sys_plugin.title = '代码生成器'
        sys_plugin.author = 'StkFish'
        sys_plugin.uuid = 'generator'
        sys_plugin.description = 'generator'
        sys_plugin.version = '1.0.1'
        sys_plugin.downloads = 12
        sys_plugin.download_url = '2'
        sys_plugin.md5_hash = '2'
        sys_plugin.price = 10.0
        sys_plugin.paid = 0
        sys_plugin.installed = 1
        sys_plugin.enabled = 1
        sys_plugin.setting_menu = '0'
        sys_plugin.status = 'normal'
        sys_plugin.created_at = datetime.fromisoformat('2025-03-10T17:09:22')
        sys_plugin.updated_at = datetime.fromisoformat('2025-05-09T09:34:40')
        db.add(sys_plugin)

        # 插入 sys_user 表数据
        sys_user = SysUser()
        sys_user.id = 1
        sys_user.user_group_id = 1
        sys_user.username = 'uuuu'
        sys_user.nickname = 'uuuu'
        sys_user.password = '$2b$12$klAmaDRXn/io90Jxjh6/2O0pfwErn9PL7CNWhWBzE2Kq9c6o83O5K'
        sys_user.email = 'dsfa@ddd.ccc'
        sys_user.mobile = '13345443233'
        sys_user.avatar = ''
        sys_user.level = 0
        sys_user.gender = 'male'
        sys_user.birthday = datetime.fromisoformat('2025-11-27')
        sys_user.bio = ''
        sys_user.balance = Decimal('0.00')
        sys_user.score = 0
        sys_user.successions = 0
        sys_user.max_successions = 0
        sys_user.prev_time = datetime.fromisoformat('2025-11-27T11:58:30')
        sys_user.login_time = datetime.fromisoformat('2025-11-27T11:58:30')
        sys_user.login_ip = ''
        sys_user.login_failure = 0
        sys_user.join_ip = ''
        sys_user.verification = ''
        sys_user.token = ''
        sys_user.status = 'normal'
        sys_user.platform = 'web'
        sys_user.created_at = datetime.fromisoformat('2025-11-27T11:58:30')
        sys_user.updated_at = datetime.fromisoformat('2025-11-27T11:58:30')
        db.add(sys_user)

        # 插入 sys_attachment_category 表数据
        sys_attachment_category = SysAttachmentCategory()
        sys_attachment_category.id = 1
        sys_attachment_category.pid = 0
        sys_attachment_category.name = 'default'
        sys_attachment_category.status = 'normal'
        sys_attachment_category.created_at = datetime.fromisoformat('2025-03-06T12:00:02')
        sys_attachment_category.updated_at = datetime.fromisoformat('2025-03-07T09:10:48')
        db.add(sys_attachment_category)

        # 插入 sys_user_group 表数据
        sys_user_group = SysUserGroup()
        sys_user_group.id = 1
        sys_user_group.pid = 0
        sys_user_group.name = 'super'
        sys_user_group.rules = {'permissions': ['all']}
        sys_user_group.access = {'permissions': ['all']}
        sys_user_group.status = 'normal'
        sys_user_group.created_at = datetime.fromisoformat('2024-04-05T12:15:11')
        sys_user_group.updated_at = datetime.fromisoformat('2025-11-19T09:29:53')
        db.add(sys_user_group)

        # 插入 sys_general_config 表数据
        sys_general_config = SysGeneralConfig()
        sys_general_config.id = 1
        sys_general_config.name = 'name'
        sys_general_config.group = 'basic'
        sys_general_config.title = 'Site name'
        sys_general_config.tip = 'Please Input  Site name'
        sys_general_config.type = 'string'
        sys_general_config.visible = ''
        sys_general_config.value = '栈鱼后台管理系统Pro 1.0'
        sys_general_config.content = ''
        sys_general_config.rule = 'required'
        sys_general_config.extend = ''
        sys_general_config.setting = ''
        sys_general_config.created_at = datetime.fromisoformat('2024-12-29T01:39:29')
        sys_general_config.updated_at = datetime.fromisoformat('2024-12-27T11:57:06')
        db.add(sys_general_config)
        sys_general_config = SysGeneralConfig()
        sys_general_config.id = 2
        sys_general_config.name = 'copyright'
        sys_general_config.group = 'basic'
        sys_general_config.title = 'Copyright'
        sys_general_config.tip = 'Please Input  Copyright'
        sys_general_config.type = 'string'
        sys_general_config.visible = ''
        sys_general_config.value = 'Copyright © 2024 <a href="https://zayum.com" class="text-subtitle-2">栈鱼后台管理系统 1.0</a>. All rights reserved.'
        sys_general_config.content = ''
        sys_general_config.rule = ''
        sys_general_config.extend = ''
        sys_general_config.setting = ''
        sys_general_config.created_at = datetime.fromisoformat('2024-12-29T01:39:29')
        sys_general_config.updated_at = datetime.fromisoformat('2024-12-27T11:57:06')
        db.add(sys_general_config)
        sys_general_config = SysGeneralConfig()
        sys_general_config.id = 3
        sys_general_config.name = 'cdnurl'
        sys_general_config.group = 'basic'
        sys_general_config.title = 'Cdn url'
        sys_general_config.tip = 'Please Input  Site name'
        sys_general_config.type = 'string'
        sys_general_config.visible = ''
        sys_general_config.value = 'https://zhanor.com'
        sys_general_config.content = ''
        sys_general_config.rule = ''
        sys_general_config.extend = ''
        sys_general_config.setting = ''
        sys_general_config.created_at = datetime.fromisoformat('2024-12-29T01:39:29')
        sys_general_config.updated_at = datetime.fromisoformat('2024-12-27T11:57:06')
        db.add(sys_general_config)
        sys_general_config = SysGeneralConfig()
        sys_general_config.id = 4
        sys_general_config.name = 'version'
        sys_general_config.group = 'basic'
        sys_general_config.title = 'Version'
        sys_general_config.tip = 'Please Input  Version'
        sys_general_config.type = 'string'
        sys_general_config.visible = ''
        sys_general_config.value = '1.0.1'
        sys_general_config.content = ''
        sys_general_config.rule = 'required'
        sys_general_config.extend = ''
        sys_general_config.setting = ''
        sys_general_config.created_at = datetime.fromisoformat('2024-12-29T01:39:29')
        sys_general_config.updated_at = datetime.fromisoformat('2024-12-27T11:57:06')
        db.add(sys_general_config)
        sys_general_config = SysGeneralConfig()
        sys_general_config.id = 5
        sys_general_config.name = 'timezone'
        sys_general_config.group = 'basic'
        sys_general_config.title = 'Timezone'
        sys_general_config.tip = ''
        sys_general_config.type = 'string'
        sys_general_config.visible = ''
        sys_general_config.value = 'Asia/Shanghai'
        sys_general_config.content = ''
        sys_general_config.rule = 'required'
        sys_general_config.extend = ''
        sys_general_config.setting = ''
        sys_general_config.created_at = datetime.fromisoformat('2024-12-29T01:39:29')
        sys_general_config.updated_at = datetime.fromisoformat('2024-12-27T11:57:06')
        db.add(sys_general_config)
        sys_general_config = SysGeneralConfig()
        sys_general_config.id = 6
        sys_general_config.name = 'forbiddenip'
        sys_general_config.group = 'basic'
        sys_general_config.title = 'Forbidden ip'
        sys_general_config.tip = 'Please Input  Forbidden ip'
        sys_general_config.type = 'text'
        sys_general_config.visible = ''
        sys_general_config.value = '12.23.21.1\n1.2.3.6\n34.78.43.1'
        sys_general_config.content = ''
        sys_general_config.rule = ''
        sys_general_config.extend = ''
        sys_general_config.setting = ''
        sys_general_config.created_at = datetime.fromisoformat('2025-04-29T07:12:13')
        sys_general_config.updated_at = datetime.fromisoformat('2025-04-29T07:12:13')
        db.add(sys_general_config)
        sys_general_config = SysGeneralConfig()
        sys_general_config.id = 7
        sys_general_config.name = 'languages'
        sys_general_config.group = 'basic'
        sys_general_config.title = 'Languages'
        sys_general_config.tip = ''
        sys_general_config.type = 'array'
        sys_general_config.visible = ''
        sys_general_config.value = '{"frontend": "zh-cn", "backend": "zh-cn"}'
        sys_general_config.content = ''
        sys_general_config.rule = 'required'
        sys_general_config.extend = ''
        sys_general_config.setting = ''
        sys_general_config.created_at = datetime.fromisoformat('2024-12-29T01:39:29')
        sys_general_config.updated_at = datetime.fromisoformat('2024-12-29T01:39:29')
        db.add(sys_general_config)
        sys_general_config = SysGeneralConfig()
        sys_general_config.id = 8
        sys_general_config.name = 'fixedpage'
        sys_general_config.group = 'basic'
        sys_general_config.title = 'Fixed page'
        sys_general_config.tip = 'Please Input Fixed page'
        sys_general_config.type = 'string'
        sys_general_config.visible = ''
        sys_general_config.value = 'dashboard'
        sys_general_config.content = ''
        sys_general_config.rule = 'required'
        sys_general_config.extend = ''
        sys_general_config.setting = ''
        sys_general_config.created_at = datetime.fromisoformat('2024-12-29T01:39:29')
        sys_general_config.updated_at = datetime.fromisoformat('2024-12-27T11:57:06')
        db.add(sys_general_config)
        sys_general_config = SysGeneralConfig()
        sys_general_config.id = 9
        sys_general_config.name = 'categorytype'
        sys_general_config.group = 'dictionary'
        sys_general_config.title = 'Category type'
        sys_general_config.tip = ''
        sys_general_config.type = 'array'
        sys_general_config.visible = ''
        sys_general_config.value = '{"default": "Default", "page": "Page", "article": "Article"}'
        sys_general_config.content = ''
        sys_general_config.rule = ''
        sys_general_config.extend = ''
        sys_general_config.setting = ''
        sys_general_config.created_at = datetime.fromisoformat('2024-12-29T01:39:29')
        sys_general_config.updated_at = datetime.fromisoformat('2024-12-27T11:57:06')
        db.add(sys_general_config)
        sys_general_config = SysGeneralConfig()
        sys_general_config.id = 10
        sys_general_config.name = 'default_category'
        sys_general_config.group = 'dictionary'
        sys_general_config.title = 'Default Category'
        sys_general_config.tip = ''
        sys_general_config.type = 'array'
        sys_general_config.visible = ''
        sys_general_config.value = '{"default": "Default"}'
        sys_general_config.content = ''
        sys_general_config.rule = ''
        sys_general_config.extend = ''
        sys_general_config.setting = ''
        sys_general_config.created_at = datetime.fromisoformat('2024-12-29T01:39:29')
        sys_general_config.updated_at = datetime.fromisoformat('2024-12-27T11:57:06')
        db.add(sys_general_config)
        sys_general_config = SysGeneralConfig()
        sys_general_config.id = 11
        sys_general_config.name = 'mail_type'
        sys_general_config.group = 'email'
        sys_general_config.title = 'Mail type'
        sys_general_config.tip = 'Please Input Mail type'
        sys_general_config.type = 'select'
        sys_general_config.visible = ''
        sys_general_config.value = 'SMTP'
        sys_general_config.content = '["Please Select","SMTP"]'
        sys_general_config.rule = ''
        sys_general_config.extend = ''
        sys_general_config.setting = ''
        sys_general_config.created_at = datetime.fromisoformat('2024-12-29T01:39:29')
        sys_general_config.updated_at = datetime.fromisoformat('2024-12-29T20:59:28')
        db.add(sys_general_config)
        sys_general_config = SysGeneralConfig()
        sys_general_config.id = 12
        sys_general_config.name = 'mail_smtp_host'
        sys_general_config.group = 'email'
        sys_general_config.title = 'Mail smtp host'
        sys_general_config.tip = 'Please Input Mail smtp host'
        sys_general_config.type = 'string'
        sys_general_config.visible = ''
        sys_general_config.value = 'smtp.qq.com'
        sys_general_config.content = ''
        sys_general_config.rule = ''
        sys_general_config.extend = ''
        sys_general_config.setting = ''
        sys_general_config.created_at = datetime.fromisoformat('2024-12-29T01:39:29')
        sys_general_config.updated_at = datetime.fromisoformat('2024-12-27T11:57:06')
        db.add(sys_general_config)
        sys_general_config = SysGeneralConfig()
        sys_general_config.id = 13
        sys_general_config.name = 'mail_smtp_port'
        sys_general_config.group = 'email'
        sys_general_config.title = 'Mail smtp port'
        sys_general_config.tip = 'Please Input  Mail smtp port(default25,SSL：465,TLS：587)'
        sys_general_config.type = 'string'
        sys_general_config.visible = ''
        sys_general_config.value = '465'
        sys_general_config.content = ''
        sys_general_config.rule = ''
        sys_general_config.extend = ''
        sys_general_config.setting = ''
        sys_general_config.created_at = datetime.fromisoformat('2024-12-29T01:39:29')
        sys_general_config.updated_at = datetime.fromisoformat('2024-12-27T11:57:06')
        db.add(sys_general_config)
        sys_general_config = SysGeneralConfig()
        sys_general_config.id = 14
        sys_general_config.name = 'mail_smtp_user'
        sys_general_config.group = 'email'
        sys_general_config.title = 'Mail smtp user'
        sys_general_config.tip = 'Please Input Mail smtp user'
        sys_general_config.type = 'string'
        sys_general_config.visible = ''
        sys_general_config.value = '10000'
        sys_general_config.content = ''
        sys_general_config.rule = ''
        sys_general_config.extend = ''
        sys_general_config.setting = ''
        sys_general_config.created_at = datetime.fromisoformat('2024-12-29T01:39:29')
        sys_general_config.updated_at = datetime.fromisoformat('2024-12-27T11:57:06')
        db.add(sys_general_config)
        sys_general_config = SysGeneralConfig()
        sys_general_config.id = 15
        sys_general_config.name = 'mail_smtp_pass'
        sys_general_config.group = 'email'
        sys_general_config.title = 'Mail smtp password'
        sys_general_config.tip = 'Please Input  Mail smtp password'
        sys_general_config.type = 'string'
        sys_general_config.visible = ''
        sys_general_config.value = 'password'
        sys_general_config.content = ''
        sys_general_config.rule = ''
        sys_general_config.extend = ''
        sys_general_config.setting = ''
        sys_general_config.created_at = datetime.fromisoformat('2024-12-29T01:39:29')
        sys_general_config.updated_at = datetime.fromisoformat('2024-12-27T11:57:06')
        db.add(sys_general_config)
        sys_general_config = SysGeneralConfig()
        sys_general_config.id = 16
        sys_general_config.name = 'mail_verify_type'
        sys_general_config.group = 'email'
        sys_general_config.title = 'Mail vertify type'
        sys_general_config.tip = 'Please Input Mail vertify type'
        sys_general_config.type = 'select'
        sys_general_config.visible = ''
        sys_general_config.value = 'TLS'
        sys_general_config.content = '["None","TLS","SSL"]'
        sys_general_config.rule = ''
        sys_general_config.extend = ''
        sys_general_config.setting = ''
        sys_general_config.created_at = datetime.fromisoformat('2024-12-29T01:39:29')
        sys_general_config.updated_at = datetime.fromisoformat('2024-12-29T20:58:05')
        db.add(sys_general_config)
        sys_general_config = SysGeneralConfig()
        sys_general_config.id = 17
        sys_general_config.name = 'mail_from'
        sys_general_config.group = 'email'
        sys_general_config.title = 'Mail from'
        sys_general_config.tip = ''
        sys_general_config.type = 'string'
        sys_general_config.visible = ''
        sys_general_config.value = '10000@qq.com'
        sys_general_config.content = ''
        sys_general_config.rule = ''
        sys_general_config.extend = ''
        sys_general_config.setting = ''
        sys_general_config.created_at = datetime.fromisoformat('2024-12-29T01:39:29')
        sys_general_config.updated_at = datetime.fromisoformat('2024-12-27T11:57:06')
        db.add(sys_general_config)
        sys_general_config = SysGeneralConfig()
        sys_general_config.id = 18
        sys_general_config.name = 'image_category'
        sys_general_config.group = 'dictionary'
        sys_general_config.title = 'Attachment Image category'
        sys_general_config.tip = ''
        sys_general_config.type = 'array'
        sys_general_config.visible = ''
        sys_general_config.value = '{"default": "Default", "blog": "Blog"}'
        sys_general_config.content = ''
        sys_general_config.rule = ''
        sys_general_config.extend = ''
        sys_general_config.setting = ''
        sys_general_config.created_at = datetime.fromisoformat('2024-12-29T01:39:29')
        sys_general_config.updated_at = datetime.fromisoformat('2024-12-29T01:39:29')
        db.add(sys_general_config)
        sys_general_config = SysGeneralConfig()
        sys_general_config.id = 19
        sys_general_config.name = 'file_category'
        sys_general_config.group = 'dictionary'
        sys_general_config.title = 'Attachment File category'
        sys_general_config.tip = ''
        sys_general_config.type = 'array'
        sys_general_config.visible = ''
        sys_general_config.value = '{"default": "Default", "product": "Product"}'
        sys_general_config.content = ''
        sys_general_config.rule = ''
        sys_general_config.extend = ''
        sys_general_config.setting = ''
        sys_general_config.created_at = datetime.fromisoformat('2024-12-29T01:39:29')
        sys_general_config.updated_at = datetime.fromisoformat('2024-12-29T01:39:29')
        db.add(sys_general_config)
        sys_general_config = SysGeneralConfig()
        sys_general_config.id = 20
        sys_general_config.name = 'video_category'
        sys_general_config.group = 'dictionary'
        sys_general_config.title = 'Attachment Video category'
        sys_general_config.tip = ''
        sys_general_config.type = 'array'
        sys_general_config.visible = ''
        sys_general_config.value = '{"default": "Default", "tutorial": "Tutorial"}'
        sys_general_config.content = ''
        sys_general_config.rule = ''
        sys_general_config.extend = ''
        sys_general_config.setting = ''
        sys_general_config.created_at = datetime.fromisoformat('2024-12-29T01:39:29')
        sys_general_config.updated_at = datetime.fromisoformat('2024-12-29T01:39:29')
        db.add(sys_general_config)
        sys_general_config = SysGeneralConfig()
        sys_general_config.id = 21
        sys_general_config.name = 'audio_category'
        sys_general_config.group = 'dictionary'
        sys_general_config.title = 'Attachment Audio category'
        sys_general_config.tip = ''
        sys_general_config.type = 'array'
        sys_general_config.visible = ''
        sys_general_config.value = '{"default": "Default", "music": "Music"}'
        sys_general_config.content = ''
        sys_general_config.rule = ''
        sys_general_config.extend = ''
        sys_general_config.setting = ''
        sys_general_config.created_at = datetime.fromisoformat('2024-12-29T01:39:29')
        sys_general_config.updated_at = datetime.fromisoformat('2024-12-29T01:39:29')
        db.add(sys_general_config)
        sys_general_config = SysGeneralConfig()
        sys_general_config.id = 22
        sys_general_config.name = 'document_category'
        sys_general_config.group = 'dictionary'
        sys_general_config.title = 'Attachment Document category'
        sys_general_config.tip = ''
        sys_general_config.type = 'array'
        sys_general_config.visible = ''
        sys_general_config.value = '{"default": "Default", "contract": "Contract"}'
        sys_general_config.content = ''
        sys_general_config.rule = ''
        sys_general_config.extend = ''
        sys_general_config.setting = ''
        sys_general_config.created_at = datetime.fromisoformat('2024-12-29T01:39:29')
        sys_general_config.updated_at = datetime.fromisoformat('2024-12-29T01:39:29')
        db.add(sys_general_config)
        sys_general_config = SysGeneralConfig()
        sys_general_config.id = 23
        sys_general_config.name = 'user_page_title'
        sys_general_config.group = 'user'
        sys_general_config.title = 'User Page Title'
        sys_general_config.tip = 'User Page Title'
        sys_general_config.type = 'string'
        sys_general_config.visible = ''
        sys_general_config.value = 'User Center'
        sys_general_config.content = ''
        sys_general_config.rule = 'letters'
        sys_general_config.extend = ''
        sys_general_config.setting = ''
        sys_general_config.created_at = datetime.fromisoformat('2024-12-29T01:39:29')
        sys_general_config.updated_at = datetime.fromisoformat('2024-12-30T12:50:59')
        db.add(sys_general_config)
        sys_general_config = SysGeneralConfig()
        sys_general_config.id = 24
        sys_general_config.name = 'user_footer'
        sys_general_config.group = 'user'
        sys_general_config.title = 'User Center Footer'
        sys_general_config.tip = 'User Center Footer'
        sys_general_config.type = 'text'
        sys_general_config.visible = ''
        sys_general_config.value = 'Copyright © 2024 <a href="https://zayum.com" class="link-secondary">会员中心</a>. All rights reserved.'
        sys_general_config.content = ''
        sys_general_config.rule = 'required'
        sys_general_config.extend = ''
        sys_general_config.setting = ''
        sys_general_config.created_at = datetime.fromisoformat('2024-12-29T01:39:29')
        sys_general_config.updated_at = datetime.fromisoformat('2024-12-30T12:50:59')
        db.add(sys_general_config)

    finally:
        db.commit()
        db.close()

if __name__ == '__main__':
    import_data()