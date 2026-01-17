-- MySQL 数据库安装脚本
-- 生成时间: 2025-11-30 10:32:13

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- 检查并创建表 sys_admin
DROP TABLE IF EXISTS `sys_admin`;

CREATE TABLE `sys_admin` (
  `id` INTEGER PRIMARY KEY AUTO_INCREMENT NOT NULL,
  `group_id` INTEGER AUTO_INCREMENT NOT NULL,
  `username` VARCHAR(20) AUTO_INCREMENT NOT NULL,
  `nickname` VARCHAR(50) AUTO_INCREMENT NOT NULL,
  `password` VARCHAR(128) AUTO_INCREMENT,
  `avatar` VARCHAR(255) AUTO_INCREMENT,
  `email` VARCHAR(100) AUTO_INCREMENT NOT NULL,
  `mobile` VARCHAR(11) AUTO_INCREMENT NOT NULL,
  `login_failure` INTEGER AUTO_INCREMENT NOT NULL,
  `login_at` DATETIME AUTO_INCREMENT,
  `login_ip` VARCHAR(50) AUTO_INCREMENT,
  `token` VARCHAR(512) AUTO_INCREMENT,
  `status` VARCHAR(6) AUTO_INCREMENT NOT NULL,
  `created_at` DATETIME AUTO_INCREMENT NOT NULL DEFAULT <function TimestampMixin.<lambda> at 0x102f98680>,
  `updated_at` DATETIME AUTO_INCREMENT NOT NULL DEFAULT <function TimestampMixin.<lambda> at 0x102f98c20>
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 插入 sys_admin 表数据
INSERT INTO `sys_admin` (`id`, `group_id`, `username`, `nickname`, `password`, `avatar`, `email`, `mobile`, `login_failure`, `login_at`, `login_ip`, `token`, `status`, `created_at`, `updated_at`) VALUES ('1', '1', 'admin', 'SupperAdmin', '$2b$12$PSRSTAdY7Vi8bFgeD5BOA.ZDozJ9rPYVklWGC6y6o7om6QWgR.WlW', '/uploads/avatar/avatar_1_c7b7e5.png', '13800000000@qq.com', '13800000000', '0', '2025-11-29T01:53:50', '127.0.0.1', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzY0OTg2MDMwfQ.RE7NJAattKcfoRKYRMUIByfllR85Dj7iXYV5j76L49U', 'normal', '2025-06-26T02:59:10', '2025-11-29T01:53:50');

-- 检查并创建表 sys_user_balance_log
DROP TABLE IF EXISTS `sys_user_balance_log`;

CREATE TABLE `sys_user_balance_log` (
  `id` INTEGER PRIMARY KEY AUTO_INCREMENT NOT NULL,
  `user_id` INTEGER AUTO_INCREMENT NOT NULL,
  `balance` DECIMAL(10, 0) AUTO_INCREMENT NOT NULL,
  `before` DECIMAL(10, 0) AUTO_INCREMENT NOT NULL,
  `after` DECIMAL(10, 0) AUTO_INCREMENT NOT NULL,
  `memo` VARCHAR(255) AUTO_INCREMENT,
  `created_at` DATETIME AUTO_INCREMENT NOT NULL DEFAULT <function TimestampMixin.<lambda> at 0x102f98680>,
  `updated_at` DATETIME AUTO_INCREMENT NOT NULL DEFAULT <function TimestampMixin.<lambda> at 0x102f98c20>
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 检查并创建表 sys_attachment
DROP TABLE IF EXISTS `sys_attachment`;

CREATE TABLE `sys_attachment` (
  `id` INTEGER PRIMARY KEY AUTO_INCREMENT NOT NULL,
  `cat_id` INTEGER AUTO_INCREMENT,
  `admin_id` INTEGER AUTO_INCREMENT NOT NULL,
  `user_id` INTEGER AUTO_INCREMENT NOT NULL,
  `att_type` VARCHAR(5) AUTO_INCREMENT,
  `thumb` VARCHAR(255) AUTO_INCREMENT,
  `path_file` VARCHAR(255) AUTO_INCREMENT NOT NULL,
  `file_name` VARCHAR(100) AUTO_INCREMENT,
  `file_size` INTEGER AUTO_INCREMENT NOT NULL,
  `mimetype` VARCHAR(100) AUTO_INCREMENT,
  `ext_param` VARCHAR(255) AUTO_INCREMENT,
  `storage` VARCHAR(100) AUTO_INCREMENT NOT NULL,
  `sha1` VARCHAR(40) AUTO_INCREMENT,
  `general_attachment_col` VARCHAR(45) AUTO_INCREMENT,
  `created_at` DATETIME AUTO_INCREMENT NOT NULL DEFAULT <function TimestampMixin.<lambda> at 0x102f98680>,
  `updated_at` DATETIME AUTO_INCREMENT NOT NULL DEFAULT <function TimestampMixin.<lambda> at 0x102f98c20>
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 检查并创建表 sys_general_category
DROP TABLE IF EXISTS `sys_general_category`;

CREATE TABLE `sys_general_category` (
  `id` INTEGER PRIMARY KEY AUTO_INCREMENT NOT NULL,
  `pid` INTEGER AUTO_INCREMENT NOT NULL,
  `type` VARCHAR(30) AUTO_INCREMENT NOT NULL,
  `name` VARCHAR(30) AUTO_INCREMENT NOT NULL,
  `thumb` VARCHAR(100) AUTO_INCREMENT,
  `keywords` VARCHAR(255) AUTO_INCREMENT,
  `description` VARCHAR(255) AUTO_INCREMENT,
  `weigh` INTEGER AUTO_INCREMENT NOT NULL,
  `status` VARCHAR(6) AUTO_INCREMENT NOT NULL,
  `created_at` DATETIME AUTO_INCREMENT NOT NULL DEFAULT <function TimestampMixin.<lambda> at 0x102f98680>,
  `updated_at` DATETIME AUTO_INCREMENT NOT NULL DEFAULT <function TimestampMixin.<lambda> at 0x102f98c20>
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 插入 sys_general_category 表数据
INSERT INTO `sys_general_category` (`id`, `pid`, `type`, `name`, `thumb`, `keywords`, `description`, `weigh`, `status`, `created_at`, `updated_at`) VALUES ('1', '0', 'default', 'default', '', '', '', '0', 'normal', '2024-05-08T17:19:06', '2025-03-07T11:50:19');
INSERT INTO `sys_general_category` (`id`, `pid`, `type`, `name`, `thumb`, `keywords`, `description`, `weigh`, `status`, `created_at`, `updated_at`) VALUES ('2', '0', 'blog', 'news', '', '', '', '0', 'normal', '2025-06-04T17:47:14', '2025-06-04T17:47:14');

-- 检查并创建表 sys_admin_rule
DROP TABLE IF EXISTS `sys_admin_rule`;

CREATE TABLE `sys_admin_rule` (
  `id` INTEGER PRIMARY KEY AUTO_INCREMENT NOT NULL,
  `rule_type` VARCHAR(6) AUTO_INCREMENT NOT NULL,
  `parent_id` INTEGER AUTO_INCREMENT,
  `name` VARCHAR(150) AUTO_INCREMENT NOT NULL,
  `path` VARCHAR(50) AUTO_INCREMENT NOT NULL,
  `component` VARCHAR(200) AUTO_INCREMENT,
  `redirect` VARCHAR(100) AUTO_INCREMENT,
  `meta` JSON AUTO_INCREMENT,
  `permission` JSON AUTO_INCREMENT,
  `menu_display_type` VARCHAR(7) AUTO_INCREMENT,
  `model_name` VARCHAR(80) AUTO_INCREMENT NOT NULL,
  `deleted_at` DATETIME AUTO_INCREMENT,
  `weigh` INTEGER AUTO_INCREMENT NOT NULL,
  `status` VARCHAR(7) AUTO_INCREMENT NOT NULL,
  `created_at` DATETIME AUTO_INCREMENT NOT NULL DEFAULT <function TimestampMixin.<lambda> at 0x102f98680>,
  `updated_at` DATETIME AUTO_INCREMENT NOT NULL DEFAULT <function TimestampMixin.<lambda> at 0x102f98c20>
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 插入 sys_admin_rule 表数据
INSERT INTO `sys_admin_rule` (`id`, `rule_type`, `parent_id`, `name`, `path`, `component`, `redirect`, `meta`, `permission`, `menu_display_type`, `model_name`, `deleted_at`, `weigh`, `status`, `created_at`, `updated_at`) VALUES ('1', 'menu', '0', 'dashboard', '/dashboard/', '/_core/dashboard/dashboard', '/dashboard', '{"icon": "mdi:view-dashboard-outline", "title": "dashboard.dashboard"}', '{}', 'addtabs', 'Dashboard', NULL, '1', 'normal', '2024-01-22T14:32:00', '2025-11-11T01:23:42');
INSERT INTO `sys_admin_rule` (`id`, `rule_type`, `parent_id`, `name`, `path`, `component`, `redirect`, `meta`, `permission`, `menu_display_type`, `model_name`, `deleted_at`, `weigh`, `status`, `created_at`, `updated_at`) VALUES ('2', 'menu', '1', 'workspace', '/dashboard/workspace', '/_core/dashboard/workspace/index', NULL, '{"icon": "mdi:view-dashboard-outline", "title": "dashboard.workspace.workspace"}', '{"view": true}', 'addtabs', 'Dashboard', NULL, '1', 'normal', '2024-01-22T14:32:00', '2025-06-05T00:22:17');
INSERT INTO `sys_admin_rule` (`id`, `rule_type`, `parent_id`, `name`, `path`, `component`, `redirect`, `meta`, `permission`, `menu_display_type`, `model_name`, `deleted_at`, `weigh`, `status`, `created_at`, `updated_at`) VALUES ('3', 'menu', '0', 'generals', '/generals', NULL, NULL, '{"icon": "mdi:cog-outline", "title": "general.general"}', '{}', 'addtabs', 'Generals', NULL, '2', 'normal', '2024-01-22T14:32:00', '2025-02-28T18:40:34');
INSERT INTO `sys_admin_rule` (`id`, `rule_type`, `parent_id`, `name`, `path`, `component`, `redirect`, `meta`, `permission`, `menu_display_type`, `model_name`, `deleted_at`, `weigh`, `status`, `created_at`, `updated_at`) VALUES ('4', 'menu', '3', 'general.profile', '/general/profile', '/_core/general/profile', NULL, '{"icon": "mdi:account-outline", "title": "general.profile.profile"}', '{"edit": true}', 'addtabs', 'GeneralProfile', NULL, '11', 'normal', '2024-01-22T14:32:00', '2025-02-28T12:04:00');
INSERT INTO `sys_admin_rule` (`id`, `rule_type`, `parent_id`, `name`, `path`, `component`, `redirect`, `meta`, `permission`, `menu_display_type`, `model_name`, `deleted_at`, `weigh`, `status`, `created_at`, `updated_at`) VALUES ('5', 'menu', '3', 'general.category', '/general/category', '/_core/general/category', '', '{"icon": "mdi:category-plus-outline", "title": "general.category.category", "menuVisibleWithForbidden": "false"}', '{"add": true, "edit": true, "view": true, "delete": true}', 'ajax', 'GeneralsCategory', NULL, '0', 'normal', '2025-03-04T03:24:40', '2025-03-07T11:12:12');
INSERT INTO `sys_admin_rule` (`id`, `rule_type`, `parent_id`, `name`, `path`, `component`, `redirect`, `meta`, `permission`, `menu_display_type`, `model_name`, `deleted_at`, `weigh`, `status`, `created_at`, `updated_at`) VALUES ('6', 'menu', '3', 'general.config', '/general/config', '/_core/general/config', NULL, '{"icon": "mdi:cog-outline", "title": "general.config.config"}', '{"add": true, "edit": true, "delete": true}', 'addtabs', 'GeneralConfig', NULL, '8', 'normal', '2024-01-22T14:32:00', '2025-03-04T07:36:31');
INSERT INTO `sys_admin_rule` (`id`, `rule_type`, `parent_id`, `name`, `path`, `component`, `redirect`, `meta`, `permission`, `menu_display_type`, `model_name`, `deleted_at`, `weigh`, `status`, `created_at`, `updated_at`) VALUES ('7', 'menu', '0', 'attachments', '/attachments', NULL, NULL, '{"icon": "mdi:paperclip", "title": "attachment.attachment_manage"}', '{}', 'blank', 'Attachment', NULL, '9', 'normal', '2024-01-22T14:32:00', '2025-03-06T11:39:00');
INSERT INTO `sys_admin_rule` (`id`, `rule_type`, `parent_id`, `name`, `path`, `component`, `redirect`, `meta`, `permission`, `menu_display_type`, `model_name`, `deleted_at`, `weigh`, `status`, `created_at`, `updated_at`) VALUES ('8', 'menu', '7', 'attachment.attachment', '/attachment/attachment', '/_core/attachment/attachment', NULL, '{"icon": "mdi:file-outline", "title": "attachment.attachment"}', '{"add": true, "edit": true, "view": true, "delete": true}', 'addtabs', 'Attachment', NULL, '10', 'normal', '2024-01-22T14:32:00', '2025-03-06T11:39:00');
INSERT INTO `sys_admin_rule` (`id`, `rule_type`, `parent_id`, `name`, `path`, `component`, `redirect`, `meta`, `permission`, `menu_display_type`, `model_name`, `deleted_at`, `weigh`, `status`, `created_at`, `updated_at`) VALUES ('9', 'menu', '0', 'plugins', '/plugins', NULL, NULL, '{"icon": "mdi:puzzle-outline", "title": "plugin.plugin", "childComponent": "/_core/general/profile"}', '{}', 'addtabs', 'Plugin', NULL, '3', 'normal', '2024-01-22T14:32:00', '2025-02-28T17:51:12');
INSERT INTO `sys_admin_rule` (`id`, `rule_type`, `parent_id`, `name`, `path`, `component`, `redirect`, `meta`, `permission`, `menu_display_type`, `model_name`, `deleted_at`, `weigh`, `status`, `created_at`, `updated_at`) VALUES ('10', 'menu', '0', 'admin', '/admin', NULL, NULL, '{"icon": "mdi:shield-account-outline", "title": "admin.admin.field.admin"}', '{}', 'addtabs', 'Admin', NULL, '4', 'normal', '2024-01-22T14:32:00', '2025-06-04T12:15:36');
INSERT INTO `sys_admin_rule` (`id`, `rule_type`, `parent_id`, `name`, `path`, `component`, `redirect`, `meta`, `permission`, `menu_display_type`, `model_name`, `deleted_at`, `weigh`, `status`, `created_at`, `updated_at`) VALUES ('11', 'menu', '10', 'admin.admin', '/admin/admin', '/_core/admin/admin', NULL, '{"icon": "mdi:account-outline", "title": "admin.admin.admin_manage"}', '{"add": true, "ajax": true, "edit": true, "view": true, "delete": true}', 'addtabs', 'Admin', NULL, '20', 'normal', '2024-01-22T14:32:00', '2025-03-06T16:24:24');
INSERT INTO `sys_admin_rule` (`id`, `rule_type`, `parent_id`, `name`, `path`, `component`, `redirect`, `meta`, `permission`, `menu_display_type`, `model_name`, `deleted_at`, `weigh`, `status`, `created_at`, `updated_at`) VALUES ('12', 'menu', '10', 'admin.group', '/admin/group', '/_core/admin/group', NULL, '{"icon": "mdi:account-group-outline", "title": "admin.group.group"}', '{"add": true, "ajax": true, "edit": true, "view": true, "delete": true}', 'addtabs', 'AdminGroup', NULL, '21', 'normal', '2024-01-22T14:32:00', '2025-03-06T13:03:05');
INSERT INTO `sys_admin_rule` (`id`, `rule_type`, `parent_id`, `name`, `path`, `component`, `redirect`, `meta`, `permission`, `menu_display_type`, `model_name`, `deleted_at`, `weigh`, `status`, `created_at`, `updated_at`) VALUES ('13', 'menu', '10', 'admin.rule', '/admin/rule', '/_core/admin/rule', NULL, '{"icon": "mdi:shield-account-outline", "title": "admin.rule.rule"}', '{"add": true, "edit": true, "view": true, "delete": true}', 'addtabs', 'AdminRule', NULL, '47', 'normal', '2024-01-22T14:32:00', '2025-03-06T13:03:05');
INSERT INTO `sys_admin_rule` (`id`, `rule_type`, `parent_id`, `name`, `path`, `component`, `redirect`, `meta`, `permission`, `menu_display_type`, `model_name`, `deleted_at`, `weigh`, `status`, `created_at`, `updated_at`) VALUES ('14', 'menu', '10', 'admin.log', '/admin/log', '/_core/admin/log', NULL, '{"icon": "mdi:clipboard-text-outline", "title": "admin.log.log"}', '{"view": true}', 'addtabs', 'AdminLog', NULL, '50', 'normal', '2024-01-22T14:32:00', '2025-03-04T07:36:31');
INSERT INTO `sys_admin_rule` (`id`, `rule_type`, `parent_id`, `name`, `path`, `component`, `redirect`, `meta`, `permission`, `menu_display_type`, `model_name`, `deleted_at`, `weigh`, `status`, `created_at`, `updated_at`) VALUES ('15', 'menu', '0', 'users', '/users', NULL, NULL, '{"icon": "mdi:account-multiple-outline", "title": "user.user"}', '{}', 'addtabs', 'Users', NULL, '24', 'normal', '2024-01-22T14:32:00', '2025-02-26T17:47:48');
INSERT INTO `sys_admin_rule` (`id`, `rule_type`, `parent_id`, `name`, `path`, `component`, `redirect`, `meta`, `permission`, `menu_display_type`, `model_name`, `deleted_at`, `weigh`, `status`, `created_at`, `updated_at`) VALUES ('16', 'menu', '15', 'user', '/user', '/_core/user/user', NULL, '{"icon": "mdi:account-outline", "title": "user.user_manage"}', '{"add": true, "edit": true, "view": true, "delete": true}', 'addtabs', 'User', NULL, '24', 'normal', '2024-01-22T14:32:00', '2025-03-06T16:19:59');
INSERT INTO `sys_admin_rule` (`id`, `rule_type`, `parent_id`, `name`, `path`, `component`, `redirect`, `meta`, `permission`, `menu_display_type`, `model_name`, `deleted_at`, `weigh`, `status`, `created_at`, `updated_at`) VALUES ('17', 'menu', '15', 'user.rule', '/user/rule', '/_core/user/rule', NULL, '{"icon": "mdi:shield-account-outline", "title": "user.rule.rule"}', '{"add": true, "edit": true, "view": true, "delete": true}', 'addtabs', 'UserRule', NULL, '26', 'normal', '2024-01-22T14:32:00', '2025-03-04T07:36:31');
INSERT INTO `sys_admin_rule` (`id`, `rule_type`, `parent_id`, `name`, `path`, `component`, `redirect`, `meta`, `permission`, `menu_display_type`, `model_name`, `deleted_at`, `weigh`, `status`, `created_at`, `updated_at`) VALUES ('18', 'menu', '15', 'user.balance.log', '/user/balance/log', '/_core/user/balance_log', NULL, '{"icon": "mdi:account-balance-wallet-outline", "title": "user.balance_log.balance_log"}', '{"add": true, "edit": true, "view": true, "delete": true}', 'addtabs', 'UserBalance', NULL, '25', 'normal', '2024-01-22T14:32:00', '2025-03-06T16:27:28');
INSERT INTO `sys_admin_rule` (`id`, `rule_type`, `parent_id`, `name`, `path`, `component`, `redirect`, `meta`, `permission`, `menu_display_type`, `model_name`, `deleted_at`, `weigh`, `status`, `created_at`, `updated_at`) VALUES ('19', 'menu', '15', 'user.score.log', '/user/score/log', '/_core/user/score_log', NULL, '{"icon": "mdi:scoreboard-outline", "title": "user.score_log.score_log"}', '{"add": true, "edit": true, "view": true, "delete": true}', 'addtabs', 'UserScore', NULL, '25', 'normal', '2024-01-22T14:32:00', '2025-03-06T16:28:37');
INSERT INTO `sys_admin_rule` (`id`, `rule_type`, `parent_id`, `name`, `path`, `component`, `redirect`, `meta`, `permission`, `menu_display_type`, `model_name`, `deleted_at`, `weigh`, `status`, `created_at`, `updated_at`) VALUES ('20', 'menu', '15', 'user.group', '/user/group', '/_core/user/group', NULL, '{"icon": "mdi:account-group-outline", "title": "user.group.group"}', '{"add": true, "edit": true, "view": true, "delete": true}', 'addtabs', 'UserGroup', NULL, '0', 'normal', '2024-09-26T13:01:14', '2025-03-04T07:36:31');
INSERT INTO `sys_admin_rule` (`id`, `rule_type`, `parent_id`, `name`, `path`, `component`, `redirect`, `meta`, `permission`, `menu_display_type`, `model_name`, `deleted_at`, `weigh`, `status`, `created_at`, `updated_at`) VALUES ('22', 'menu', '9', 'generator', '/plugins/generator', '/plugins/generator', '', '{"icon": "mdi:codepen", "title": "generator.code_generator", "menuVisibleWithForbidden": "false"}', '{"view": true}', 'ajax', 'generator', NULL, '0', 'normal', '2025-02-28T10:31:33', '2025-03-04T07:36:31');
INSERT INTO `sys_admin_rule` (`id`, `rule_type`, `parent_id`, `name`, `path`, `component`, `redirect`, `meta`, `permission`, `menu_display_type`, `model_name`, `deleted_at`, `weigh`, `status`, `created_at`, `updated_at`) VALUES ('24', 'menu', '7', 'attachmentCategory', '/attachment/category', '/_core/attachment/category', '', '{"icon": "mdi:attachment", "title": "attachment.category.category", "menuVisibleWithForbidden": "false"}', '{"add": true, "edit": true, "view": true, "delete": true}', 'ajax', 'attachmentCategory', NULL, '0', 'normal', '2025-03-06T03:54:07', '2025-03-06T12:56:31');
INSERT INTO `sys_admin_rule` (`id`, `rule_type`, `parent_id`, `name`, `path`, `component`, `redirect`, `meta`, `permission`, `menu_display_type`, `model_name`, `deleted_at`, `weigh`, `status`, `created_at`, `updated_at`) VALUES ('25', 'menu', '9', 'plugin', '/plugin/plugin', '/_core/plugin/plugin', '', '{"icon": "mdi:shape-rectangle-add", "title": "plugin.plugin", "menuVisibleWithForbidden": "false"}', '{"add": true, "edit": true, "view": true, "delete": true}', 'ajax', 'plugin', NULL, '0', 'normal', '2025-03-09T02:40:04', '2025-03-09T11:05:32');
INSERT INTO `sys_admin_rule` (`id`, `rule_type`, `parent_id`, `name`, `path`, `component`, `redirect`, `meta`, `permission`, `menu_display_type`, `model_name`, `deleted_at`, `weigh`, `status`, `created_at`, `updated_at`) VALUES ('26', 'menu', '9', 'plugin_store', '/plugin/plugin_store', '/_core/plugin_store', '', '{"icon": "mdi:all-inclusive", "title": "plugin.plugin_store", "menuVisibleWithForbidden": "false"}', '{"enable": true, "disable": true, "install": true, "unstall": true}', 'ajax', 'online_plugin', NULL, '0', 'normal', '2025-03-10T07:15:54', '2025-03-10T16:07:41');
INSERT INTO `sys_admin_rule` (`id`, `rule_type`, `parent_id`, `name`, `path`, `component`, `redirect`, `meta`, `permission`, `menu_display_type`, `model_name`, `deleted_at`, `weigh`, `status`, `created_at`, `updated_at`) VALUES ('27', 'menu', '1', 'analytics', '/dashboard/analytics', '/_core/dashboard/analytics/index', NULL, '{"icon": "mdi:view-dashboard-outline", "title": "dashboard.analytics"}', '{"view": true}', 'addtabs', 'Dashboard', NULL, '1', 'normal', '2024-01-22T14:32:00', '2025-03-04T07:36:31');

-- 检查并创建表 sys_notification
DROP TABLE IF EXISTS `sys_notification`;

CREATE TABLE `sys_notification` (
  `id` INTEGER PRIMARY KEY AUTO_INCREMENT NOT NULL,
  `receiver_id` INTEGER AUTO_INCREMENT NOT NULL,
  `receiver_type` VARCHAR(20) AUTO_INCREMENT NOT NULL,
  `sender_id` INTEGER AUTO_INCREMENT,
  `sender_name` VARCHAR(50) AUTO_INCREMENT,
  `title` VARCHAR(100) AUTO_INCREMENT NOT NULL,
  `message` TEXT AUTO_INCREMENT NOT NULL,
  `type` VARCHAR(8) AUTO_INCREMENT NOT NULL,
  `status` VARCHAR(6) AUTO_INCREMENT NOT NULL,
  `avatar` VARCHAR(255) AUTO_INCREMENT,
  `related_id` INTEGER AUTO_INCREMENT,
  `related_type` VARCHAR(50) AUTO_INCREMENT,
  `related_url` VARCHAR(500) AUTO_INCREMENT,
  `priority` INTEGER AUTO_INCREMENT NOT NULL,
  `expires_at` DATETIME AUTO_INCREMENT,
  `created_at` DATETIME AUTO_INCREMENT NOT NULL DEFAULT <function TimestampMixin.<lambda> at 0x102f98680>,
  `updated_at` DATETIME AUTO_INCREMENT NOT NULL DEFAULT <function TimestampMixin.<lambda> at 0x102f98c20>
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 检查并创建表 sys_admin_log
DROP TABLE IF EXISTS `sys_admin_log`;

CREATE TABLE `sys_admin_log` (
  `id` INTEGER PRIMARY KEY AUTO_INCREMENT NOT NULL,
  `admin_id` INTEGER AUTO_INCREMENT NOT NULL,
  `username` VARCHAR(30) AUTO_INCREMENT NOT NULL,
  `url` VARCHAR(1500) AUTO_INCREMENT NOT NULL,
  `title` VARCHAR(100) AUTO_INCREMENT,
  `content` TEXT AUTO_INCREMENT NOT NULL,
  `ip` VARCHAR(50) AUTO_INCREMENT NOT NULL,
  `useragent` TEXT AUTO_INCREMENT,
  `created_at` DATETIME AUTO_INCREMENT NOT NULL DEFAULT <function TimestampMixin.<lambda> at 0x102f98680>,
  `updated_at` DATETIME AUTO_INCREMENT NOT NULL DEFAULT <function TimestampMixin.<lambda> at 0x102f98c20>
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 插入 sys_admin_log 表数据
INSERT INTO `sys_admin_log` (`id`, `admin_id`, `username`, `url`, `title`, `content`, `ip`, `useragent`, `created_at`, `updated_at`) VALUES ('1', '1', 'admin', 'http://127.0.0.1:8000/api/admin/user/create', 'POST', '{"user_group_id": 1, "username": "uuuu", "nickname": "uuuu", "password": "*", "email": "dsfa@ddd.ccc", "mobile": "13345443233", "avatar": "", "level": 0, "gender": "male", "birthday": "2025-11-27", "bio": "", "balance": 0, "score": 0, "successions": 0, "max_successions": 0, "prev_time": "2025-11-27 11:58:30", "login_time": "2025-11-27 11:58:30", "login_ip": "", "login_failure": 0, "join_ip": "", "verification": "", "token": "", "status": "normal", "platform": "web", "created_at": "2025-11-27 11:58:30", "updated_at": "2025-11-27 11:58:30"}', '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36', '2025-11-27T03:59:30', '2025-11-27T03:59:30');
INSERT INTO `sys_admin_log` (`id`, `admin_id`, `username`, `url`, `title`, `content`, `ip`, `useragent`, `created_at`, `updated_at`) VALUES ('2', '1', 'admin', 'http://127.0.0.1:8000/api/admin/admin/update/1', 'PUT', '{"id": 1, "group_id": 1, "username": "admin", "nickname": "SupperAdmin", "avatar": "/uploads/avatar/avatar_1_c7b7e5.png", "email": "13800000000@qq.com", "mobile": "13800000000", "login_failure": 0, "login_at": "2025-11-29 01:26:27", "login_ip": "127.0.0.1", "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzY0OTg0Mzg3fQ.6kogc16gtD9ipLIr7eqrwgBCRQvtSdkBTx5VvFJF6oQ", "status": "normal", "created_at": "2025-06-26 02:59:10", "updated_at": "2025-11-29 01:26:27", "password": "*"}', '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36', '2025-11-29T01:53:39', '2025-11-29T01:53:39');

-- 检查并创建表 sys_user_rule
DROP TABLE IF EXISTS `sys_user_rule`;

CREATE TABLE `sys_user_rule` (
  `id` INTEGER PRIMARY KEY AUTO_INCREMENT NOT NULL,
  `rule_type` VARCHAR(6) AUTO_INCREMENT NOT NULL,
  `parent_id` INTEGER AUTO_INCREMENT NOT NULL,
  `name` VARCHAR(150) AUTO_INCREMENT NOT NULL,
  `path` VARCHAR(50) AUTO_INCREMENT NOT NULL,
  `component` VARCHAR(200) AUTO_INCREMENT,
  `redirect` VARCHAR(100) AUTO_INCREMENT,
  `meta` JSON AUTO_INCREMENT,
  `permission` JSON AUTO_INCREMENT,
  `menu_display_type` VARCHAR(7) AUTO_INCREMENT,
  `model_name` VARCHAR(80) AUTO_INCREMENT NOT NULL,
  `deleted_at` DATETIME AUTO_INCREMENT,
  `weigh` INTEGER AUTO_INCREMENT NOT NULL,
  `status` VARCHAR(7) AUTO_INCREMENT NOT NULL,
  `created_at` DATETIME AUTO_INCREMENT NOT NULL DEFAULT <function TimestampMixin.<lambda> at 0x102f98680>,
  `updated_at` DATETIME AUTO_INCREMENT NOT NULL DEFAULT <function TimestampMixin.<lambda> at 0x102f98c20>
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 插入 sys_user_rule 表数据
INSERT INTO `sys_user_rule` (`id`, `rule_type`, `parent_id`, `name`, `path`, `component`, `redirect`, `meta`, `permission`, `menu_display_type`, `model_name`, `deleted_at`, `weigh`, `status`, `created_at`, `updated_at`) VALUES ('1', 'menu', '0', 'userHome', '/home', '/user/home', '/dashboard', '{"icon": "mdi:home", "title": "home.home"}', '{}', 'addtabs', 'Home', NULL, '1', 'normal', '2024-01-22T14:32:00', '2025-07-01T09:21:36');
INSERT INTO `sys_user_rule` (`id`, `rule_type`, `parent_id`, `name`, `path`, `component`, `redirect`, `meta`, `permission`, `menu_display_type`, `model_name`, `deleted_at`, `weigh`, `status`, `created_at`, `updated_at`) VALUES ('2', 'menu', '0', 'userProfile', '/profile', '/user/profile', NULL, '{"icon": "mdi:account", "title": "profile.profile"}', '{}', 'addtabs', 'Profile', NULL, '1', 'normal', '2024-01-22T14:32:00', '2025-07-01T09:22:00');
INSERT INTO `sys_user_rule` (`id`, `rule_type`, `parent_id`, `name`, `path`, `component`, `redirect`, `meta`, `permission`, `menu_display_type`, `model_name`, `deleted_at`, `weigh`, `status`, `created_at`, `updated_at`) VALUES ('3', 'menu', '0', 'userSetting', '/setting', '/user/setting', NULL, '{"icon": "mdi:cog", "title": "setting.setting"}', '{}', 'addtabs', 'Setting', NULL, '2', 'normal', '2024-01-22T14:32:00', '2025-07-01T09:21:36');

-- 检查并创建表 sys_admin_group
DROP TABLE IF EXISTS `sys_admin_group`;

CREATE TABLE `sys_admin_group` (
  `id` INTEGER PRIMARY KEY AUTO_INCREMENT NOT NULL,
  `pid` INTEGER AUTO_INCREMENT NOT NULL,
  `name` VARCHAR(100) AUTO_INCREMENT NOT NULL,
  `rules` JSON AUTO_INCREMENT NOT NULL,
  `access` JSON AUTO_INCREMENT NOT NULL,
  `status` VARCHAR(6) AUTO_INCREMENT NOT NULL,
  `created_at` DATETIME AUTO_INCREMENT NOT NULL DEFAULT <function TimestampMixin.<lambda> at 0x102f98680>,
  `updated_at` DATETIME AUTO_INCREMENT NOT NULL DEFAULT <function TimestampMixin.<lambda> at 0x102f98c20>
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 插入 sys_admin_group 表数据
INSERT INTO `sys_admin_group` (`id`, `pid`, `name`, `rules`, `access`, `status`, `created_at`, `updated_at`) VALUES ('1', '0', 'super', '["all"]', '["all"]', 'normal', '2024-04-05T12:15:11', '2025-03-04T15:54:49');

-- 检查并创建表 sys_plugin
DROP TABLE IF EXISTS `sys_plugin`;

CREATE TABLE `sys_plugin` (
  `id` INTEGER PRIMARY KEY AUTO_INCREMENT NOT NULL,
  `title` VARCHAR(120) AUTO_INCREMENT NOT NULL,
  `author` VARCHAR(80) AUTO_INCREMENT NOT NULL,
  `uuid` VARCHAR(120) AUTO_INCREMENT NOT NULL,
  `description` VARCHAR(255) AUTO_INCREMENT NOT NULL,
  `version` VARCHAR(50) AUTO_INCREMENT NOT NULL,
  `downloads` INTEGER AUTO_INCREMENT NOT NULL,
  `download_url` VARCHAR(255) AUTO_INCREMENT NOT NULL,
  `md5_hash` VARCHAR(32) AUTO_INCREMENT NOT NULL,
  `price` DECIMAL(10, 2) AUTO_INCREMENT,
  `paid` SMALLINT AUTO_INCREMENT NOT NULL,
  `installed` SMALLINT AUTO_INCREMENT NOT NULL,
  `enabled` SMALLINT AUTO_INCREMENT NOT NULL,
  `setting_menu` VARCHAR(255) AUTO_INCREMENT NOT NULL,
  `status` VARCHAR(6) AUTO_INCREMENT NOT NULL,
  `created_at` DATETIME AUTO_INCREMENT NOT NULL DEFAULT <function TimestampMixin.<lambda> at 0x102f98680>,
  `updated_at` DATETIME AUTO_INCREMENT NOT NULL DEFAULT <function TimestampMixin.<lambda> at 0x102f98c20>
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 插入 sys_plugin 表数据
INSERT INTO `sys_plugin` (`id`, `title`, `author`, `uuid`, `description`, `version`, `downloads`, `download_url`, `md5_hash`, `price`, `paid`, `installed`, `enabled`, `setting_menu`, `status`, `created_at`, `updated_at`) VALUES ('1', '代码生成器', 'StkFish', 'generator', 'generator', '1.0.1', '12', '2', '2', '10', '0', '1', '1', '0', 'normal', '2025-03-10T17:09:22', '2025-05-09T09:34:40');

-- 检查并创建表 sys_user
DROP TABLE IF EXISTS `sys_user`;

CREATE TABLE `sys_user` (
  `id` INTEGER PRIMARY KEY AUTO_INCREMENT NOT NULL,
  `user_group_id` INTEGER AUTO_INCREMENT NOT NULL,
  `username` VARCHAR(32) AUTO_INCREMENT NOT NULL,
  `nickname` VARCHAR(50) AUTO_INCREMENT NOT NULL,
  `password` VARCHAR(120) AUTO_INCREMENT,
  `email` VARCHAR(100) AUTO_INCREMENT NOT NULL,
  `mobile` VARCHAR(16) AUTO_INCREMENT NOT NULL,
  `avatar` VARCHAR(255) AUTO_INCREMENT,
  `level` SMALLINT AUTO_INCREMENT NOT NULL,
  `gender` VARCHAR(6) AUTO_INCREMENT NOT NULL,
  `birthday` DATE AUTO_INCREMENT,
  `bio` VARCHAR(100) AUTO_INCREMENT,
  `balance` DECIMAL(10, 2) AUTO_INCREMENT,
  `score` INTEGER AUTO_INCREMENT NOT NULL,
  `successions` INTEGER AUTO_INCREMENT NOT NULL,
  `max_successions` INTEGER AUTO_INCREMENT NOT NULL,
  `prev_time` DATETIME AUTO_INCREMENT,
  `login_time` DATETIME AUTO_INCREMENT,
  `login_ip` VARCHAR(50) AUTO_INCREMENT,
  `login_failure` SMALLINT AUTO_INCREMENT NOT NULL,
  `join_ip` VARCHAR(50) AUTO_INCREMENT,
  `verification` VARCHAR(255) AUTO_INCREMENT,
  `token` VARCHAR(250) AUTO_INCREMENT,
  `status` VARCHAR(6) AUTO_INCREMENT NOT NULL,
  `platform` VARCHAR(7) AUTO_INCREMENT NOT NULL,
  `created_at` DATETIME AUTO_INCREMENT NOT NULL DEFAULT <function TimestampMixin.<lambda> at 0x102f98680>,
  `updated_at` DATETIME AUTO_INCREMENT NOT NULL DEFAULT <function TimestampMixin.<lambda> at 0x102f98c20>
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 插入 sys_user 表数据
INSERT INTO `sys_user` (`id`, `user_group_id`, `username`, `nickname`, `password`, `email`, `mobile`, `avatar`, `level`, `gender`, `birthday`, `bio`, `balance`, `score`, `successions`, `max_successions`, `prev_time`, `login_time`, `login_ip`, `login_failure`, `join_ip`, `verification`, `token`, `status`, `platform`, `created_at`, `updated_at`) VALUES ('1', '1', 'uuuu', 'uuuu', '$2b$12$klAmaDRXn/io90Jxjh6/2O0pfwErn9PL7CNWhWBzE2Kq9c6o83O5K', 'dsfa@ddd.ccc', '13345443233', '', '0', 'male', '2025-11-27', '', '0.00', '0', '0', '0', '2025-11-27T11:58:30', '2025-11-27T11:58:30', '', '0', '', '', '', 'normal', 'web', '2025-11-27T11:58:30', '2025-11-27T11:58:30');

-- 检查并创建表 sys_user_score_log
DROP TABLE IF EXISTS `sys_user_score_log`;

CREATE TABLE `sys_user_score_log` (
  `id` INTEGER PRIMARY KEY AUTO_INCREMENT NOT NULL,
  `user_id` INTEGER AUTO_INCREMENT NOT NULL,
  `score` INTEGER AUTO_INCREMENT NOT NULL,
  `before` INTEGER AUTO_INCREMENT NOT NULL,
  `after` INTEGER AUTO_INCREMENT NOT NULL,
  `memo` VARCHAR(255) AUTO_INCREMENT,
  `created_at` DATETIME AUTO_INCREMENT NOT NULL DEFAULT <function TimestampMixin.<lambda> at 0x102f98680>,
  `updated_at` DATETIME AUTO_INCREMENT NOT NULL DEFAULT <function TimestampMixin.<lambda> at 0x102f98c20>
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 检查并创建表 sys_analytics_summary
DROP TABLE IF EXISTS `sys_analytics_summary`;

CREATE TABLE `sys_analytics_summary` (
  `id` VARCHAR(200) PRIMARY KEY AUTO_INCREMENT NOT NULL,
  `summary_type` VARCHAR(8) AUTO_INCREMENT NOT NULL,
  `summary_date` DATE AUTO_INCREMENT,
  `summary_year` INTEGER AUTO_INCREMENT,
  `summary_month` INTEGER AUTO_INCREMENT,
  `region_name` VARCHAR(100) AUTO_INCREMENT,
  `total_users` INTEGER AUTO_INCREMENT,
  `new_users` INTEGER AUTO_INCREMENT,
  `active_users` INTEGER AUTO_INCREMENT,
  `total_logins` INTEGER AUTO_INCREMENT,
  `total_visits` INTEGER AUTO_INCREMENT,
  `user_group_distribution` JSON AUTO_INCREMENT,
  `action_distribution` JSON AUTO_INCREMENT,
  `created_at` DATETIME AUTO_INCREMENT NOT NULL DEFAULT <function TimestampMixin.<lambda> at 0x102f98680>,
  `updated_at` DATETIME AUTO_INCREMENT NOT NULL DEFAULT <function TimestampMixin.<lambda> at 0x102f98c20>
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 检查并创建表 sys_attachment_category
DROP TABLE IF EXISTS `sys_attachment_category`;

CREATE TABLE `sys_attachment_category` (
  `id` INTEGER PRIMARY KEY AUTO_INCREMENT NOT NULL,
  `pid` INTEGER AUTO_INCREMENT NOT NULL,
  `name` VARCHAR(30) AUTO_INCREMENT NOT NULL,
  `status` VARCHAR(6) AUTO_INCREMENT NOT NULL,
  `created_at` DATETIME AUTO_INCREMENT NOT NULL DEFAULT <function TimestampMixin.<lambda> at 0x102f98680>,
  `updated_at` DATETIME AUTO_INCREMENT NOT NULL DEFAULT <function TimestampMixin.<lambda> at 0x102f98c20>
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 插入 sys_attachment_category 表数据
INSERT INTO `sys_attachment_category` (`id`, `pid`, `name`, `status`, `created_at`, `updated_at`) VALUES ('1', '0', 'default', 'normal', '2025-03-06T12:00:02', '2025-03-07T09:10:48');

-- 检查并创建表 sys_user_group
DROP TABLE IF EXISTS `sys_user_group`;

CREATE TABLE `sys_user_group` (
  `id` INTEGER PRIMARY KEY AUTO_INCREMENT NOT NULL,
  `pid` INTEGER AUTO_INCREMENT NOT NULL,
  `name` VARCHAR(100) AUTO_INCREMENT NOT NULL,
  `rules` JSON AUTO_INCREMENT NOT NULL,
  `access` JSON AUTO_INCREMENT NOT NULL,
  `status` VARCHAR(6) AUTO_INCREMENT NOT NULL,
  `created_at` DATETIME AUTO_INCREMENT NOT NULL DEFAULT <function TimestampMixin.<lambda> at 0x102f98680>,
  `updated_at` DATETIME AUTO_INCREMENT NOT NULL DEFAULT <function TimestampMixin.<lambda> at 0x102f98c20>
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 插入 sys_user_group 表数据
INSERT INTO `sys_user_group` (`id`, `pid`, `name`, `rules`, `access`, `status`, `created_at`, `updated_at`) VALUES ('1', '0', 'super', '{"permissions": ["all"]}', '{"permissions": ["all"]}', 'normal', '2024-04-05T12:15:11', '2025-11-19T09:29:53');

-- 检查并创建表 sys_general_config
DROP TABLE IF EXISTS `sys_general_config`;

CREATE TABLE `sys_general_config` (
  `id` INTEGER PRIMARY KEY AUTO_INCREMENT NOT NULL,
  `name` VARCHAR(30) AUTO_INCREMENT NOT NULL,
  `group` VARCHAR(30) AUTO_INCREMENT NOT NULL,
  `title` VARCHAR(100) AUTO_INCREMENT NOT NULL,
  `tip` VARCHAR(100) AUTO_INCREMENT,
  `type` VARCHAR(30) AUTO_INCREMENT,
  `visible` VARCHAR(255) AUTO_INCREMENT,
  `value` TEXT AUTO_INCREMENT,
  `content` TEXT AUTO_INCREMENT,
  `rule` VARCHAR(100) AUTO_INCREMENT,
  `extend` VARCHAR(255) AUTO_INCREMENT,
  `setting` VARCHAR(255) AUTO_INCREMENT,
  `created_at` DATETIME AUTO_INCREMENT NOT NULL DEFAULT <function TimestampMixin.<lambda> at 0x102f98680>,
  `updated_at` DATETIME AUTO_INCREMENT NOT NULL DEFAULT <function TimestampMixin.<lambda> at 0x102f98c20>
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 插入 sys_general_config 表数据
INSERT INTO `sys_general_config` (`id`, `name`, `group`, `title`, `tip`, `type`, `visible`, `value`, `content`, `rule`, `extend`, `setting`, `created_at`, `updated_at`) VALUES ('1', 'name', 'basic', 'Site name', 'Please Input  Site name', 'string', '', '栈鱼后台管理系统Pro 1.0', '', 'required', '', '', '2024-12-29T01:39:29', '2024-12-27T11:57:06');
INSERT INTO `sys_general_config` (`id`, `name`, `group`, `title`, `tip`, `type`, `visible`, `value`, `content`, `rule`, `extend`, `setting`, `created_at`, `updated_at`) VALUES ('2', 'copyright', 'basic', 'Copyright', 'Please Input  Copyright', 'string', '', 'Copyright © 2024 <a href="https://zayum.com" class="text-subtitle-2">栈鱼后台管理系统 1.0</a>. All rights reserved.', '', '', '', '', '2024-12-29T01:39:29', '2024-12-27T11:57:06');
INSERT INTO `sys_general_config` (`id`, `name`, `group`, `title`, `tip`, `type`, `visible`, `value`, `content`, `rule`, `extend`, `setting`, `created_at`, `updated_at`) VALUES ('3', 'cdnurl', 'basic', 'Cdn url', 'Please Input  Site name', 'string', '', 'https://zhanor.com', '', '', '', '', '2024-12-29T01:39:29', '2024-12-27T11:57:06');
INSERT INTO `sys_general_config` (`id`, `name`, `group`, `title`, `tip`, `type`, `visible`, `value`, `content`, `rule`, `extend`, `setting`, `created_at`, `updated_at`) VALUES ('4', 'version', 'basic', 'Version', 'Please Input  Version', 'string', '', '1.0.1', '', 'required', '', '', '2024-12-29T01:39:29', '2024-12-27T11:57:06');
INSERT INTO `sys_general_config` (`id`, `name`, `group`, `title`, `tip`, `type`, `visible`, `value`, `content`, `rule`, `extend`, `setting`, `created_at`, `updated_at`) VALUES ('5', 'timezone', 'basic', 'Timezone', '', 'string', '', 'Asia/Shanghai', '', 'required', '', '', '2024-12-29T01:39:29', '2024-12-27T11:57:06');
INSERT INTO `sys_general_config` (`id`, `name`, `group`, `title`, `tip`, `type`, `visible`, `value`, `content`, `rule`, `extend`, `setting`, `created_at`, `updated_at`) VALUES ('6', 'forbiddenip', 'basic', 'Forbidden ip', 'Please Input  Forbidden ip', 'text', '', '12.23.21.1
1.2.3.6
34.78.43.1', '', '', '', '', '2025-04-29T07:12:13', '2025-04-29T07:12:13');
INSERT INTO `sys_general_config` (`id`, `name`, `group`, `title`, `tip`, `type`, `visible`, `value`, `content`, `rule`, `extend`, `setting`, `created_at`, `updated_at`) VALUES ('7', 'languages', 'basic', 'Languages', '', 'array', '', '{"frontend": "zh-cn", "backend": "zh-cn"}', '', 'required', '', '', '2024-12-29T01:39:29', '2024-12-29T01:39:29');
INSERT INTO `sys_general_config` (`id`, `name`, `group`, `title`, `tip`, `type`, `visible`, `value`, `content`, `rule`, `extend`, `setting`, `created_at`, `updated_at`) VALUES ('8', 'fixedpage', 'basic', 'Fixed page', 'Please Input Fixed page', 'string', '', 'dashboard', '', 'required', '', '', '2024-12-29T01:39:29', '2024-12-27T11:57:06');
INSERT INTO `sys_general_config` (`id`, `name`, `group`, `title`, `tip`, `type`, `visible`, `value`, `content`, `rule`, `extend`, `setting`, `created_at`, `updated_at`) VALUES ('9', 'categorytype', 'dictionary', 'Category type', '', 'array', '', '{"default": "Default", "page": "Page", "article": "Article"}', '', '', '', '', '2024-12-29T01:39:29', '2024-12-27T11:57:06');
INSERT INTO `sys_general_config` (`id`, `name`, `group`, `title`, `tip`, `type`, `visible`, `value`, `content`, `rule`, `extend`, `setting`, `created_at`, `updated_at`) VALUES ('10', 'default_category', 'dictionary', 'Default Category', '', 'array', '', '{"default": "Default"}', '', '', '', '', '2024-12-29T01:39:29', '2024-12-27T11:57:06');
INSERT INTO `sys_general_config` (`id`, `name`, `group`, `title`, `tip`, `type`, `visible`, `value`, `content`, `rule`, `extend`, `setting`, `created_at`, `updated_at`) VALUES ('11', 'mail_type', 'email', 'Mail type', 'Please Input Mail type', 'select', '', 'SMTP', '["Please Select","SMTP"]', '', '', '', '2024-12-29T01:39:29', '2024-12-29T20:59:28');
INSERT INTO `sys_general_config` (`id`, `name`, `group`, `title`, `tip`, `type`, `visible`, `value`, `content`, `rule`, `extend`, `setting`, `created_at`, `updated_at`) VALUES ('12', 'mail_smtp_host', 'email', 'Mail smtp host', 'Please Input Mail smtp host', 'string', '', 'smtp.qq.com', '', '', '', '', '2024-12-29T01:39:29', '2024-12-27T11:57:06');
INSERT INTO `sys_general_config` (`id`, `name`, `group`, `title`, `tip`, `type`, `visible`, `value`, `content`, `rule`, `extend`, `setting`, `created_at`, `updated_at`) VALUES ('13', 'mail_smtp_port', 'email', 'Mail smtp port', 'Please Input  Mail smtp port(default25,SSL：465,TLS：587)', 'string', '', '465', '', '', '', '', '2024-12-29T01:39:29', '2024-12-27T11:57:06');
INSERT INTO `sys_general_config` (`id`, `name`, `group`, `title`, `tip`, `type`, `visible`, `value`, `content`, `rule`, `extend`, `setting`, `created_at`, `updated_at`) VALUES ('14', 'mail_smtp_user', 'email', 'Mail smtp user', 'Please Input Mail smtp user', 'string', '', '10000', '', '', '', '', '2024-12-29T01:39:29', '2024-12-27T11:57:06');
INSERT INTO `sys_general_config` (`id`, `name`, `group`, `title`, `tip`, `type`, `visible`, `value`, `content`, `rule`, `extend`, `setting`, `created_at`, `updated_at`) VALUES ('15', 'mail_smtp_pass', 'email', 'Mail smtp password', 'Please Input  Mail smtp password', 'string', '', 'password', '', '', '', '', '2024-12-29T01:39:29', '2024-12-27T11:57:06');
INSERT INTO `sys_general_config` (`id`, `name`, `group`, `title`, `tip`, `type`, `visible`, `value`, `content`, `rule`, `extend`, `setting`, `created_at`, `updated_at`) VALUES ('16', 'mail_verify_type', 'email', 'Mail vertify type', 'Please Input Mail vertify type', 'select', '', 'TLS', '["None","TLS","SSL"]', '', '', '', '2024-12-29T01:39:29', '2024-12-29T20:58:05');
INSERT INTO `sys_general_config` (`id`, `name`, `group`, `title`, `tip`, `type`, `visible`, `value`, `content`, `rule`, `extend`, `setting`, `created_at`, `updated_at`) VALUES ('17', 'mail_from', 'email', 'Mail from', '', 'string', '', '10000@qq.com', '', '', '', '', '2024-12-29T01:39:29', '2024-12-27T11:57:06');
INSERT INTO `sys_general_config` (`id`, `name`, `group`, `title`, `tip`, `type`, `visible`, `value`, `content`, `rule`, `extend`, `setting`, `created_at`, `updated_at`) VALUES ('18', 'image_category', 'dictionary', 'Attachment Image category', '', 'array', '', '{"default": "Default", "blog": "Blog"}', '', '', '', '', '2024-12-29T01:39:29', '2024-12-29T01:39:29');
INSERT INTO `sys_general_config` (`id`, `name`, `group`, `title`, `tip`, `type`, `visible`, `value`, `content`, `rule`, `extend`, `setting`, `created_at`, `updated_at`) VALUES ('19', 'file_category', 'dictionary', 'Attachment File category', '', 'array', '', '{"default": "Default", "product": "Product"}', '', '', '', '', '2024-12-29T01:39:29', '2024-12-29T01:39:29');
INSERT INTO `sys_general_config` (`id`, `name`, `group`, `title`, `tip`, `type`, `visible`, `value`, `content`, `rule`, `extend`, `setting`, `created_at`, `updated_at`) VALUES ('20', 'video_category', 'dictionary', 'Attachment Video category', '', 'array', '', '{"default": "Default", "tutorial": "Tutorial"}', '', '', '', '', '2024-12-29T01:39:29', '2024-12-29T01:39:29');
INSERT INTO `sys_general_config` (`id`, `name`, `group`, `title`, `tip`, `type`, `visible`, `value`, `content`, `rule`, `extend`, `setting`, `created_at`, `updated_at`) VALUES ('21', 'audio_category', 'dictionary', 'Attachment Audio category', '', 'array', '', '{"default": "Default", "music": "Music"}', '', '', '', '', '2024-12-29T01:39:29', '2024-12-29T01:39:29');
INSERT INTO `sys_general_config` (`id`, `name`, `group`, `title`, `tip`, `type`, `visible`, `value`, `content`, `rule`, `extend`, `setting`, `created_at`, `updated_at`) VALUES ('22', 'document_category', 'dictionary', 'Attachment Document category', '', 'array', '', '{"default": "Default", "contract": "Contract"}', '', '', '', '', '2024-12-29T01:39:29', '2024-12-29T01:39:29');
INSERT INTO `sys_general_config` (`id`, `name`, `group`, `title`, `tip`, `type`, `visible`, `value`, `content`, `rule`, `extend`, `setting`, `created_at`, `updated_at`) VALUES ('23', 'user_page_title', 'user', 'User Page Title', 'User Page Title', 'string', '', 'User Center', '', 'letters', '', '', '2024-12-29T01:39:29', '2024-12-30T12:50:59');
INSERT INTO `sys_general_config` (`id`, `name`, `group`, `title`, `tip`, `type`, `visible`, `value`, `content`, `rule`, `extend`, `setting`, `created_at`, `updated_at`) VALUES ('24', 'user_footer', 'user', 'User Center Footer', 'User Center Footer', 'text', '', 'Copyright © 2024 <a href="https://zayum.com" class="link-secondary">会员中心</a>. All rights reserved.', '', 'required', '', '', '2024-12-29T01:39:29', '2024-12-30T12:50:59');

SET FOREIGN_KEY_CHECKS = 1;