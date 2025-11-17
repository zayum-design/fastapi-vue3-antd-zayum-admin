-- 系统通知表
-- 用于存储系统通知、消息通知、评论通知、任务提醒等

CREATE TABLE IF NOT EXISTS `sys_notification` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `receiver_id` int NOT NULL COMMENT '接收者ID',
  `receiver_type` varchar(20) NOT NULL DEFAULT 'admin' COMMENT '接收者类型: admin/user',
  `sender_id` int DEFAULT NULL COMMENT '发送者ID',
  `sender_name` varchar(50) DEFAULT NULL COMMENT '发送者名称',
  `title` varchar(100) NOT NULL COMMENT '通知标题',
  `message` text NOT NULL COMMENT '通知内容',
  `type` enum('system','message','comment','reminder','approval','security','update','task') NOT NULL DEFAULT 'system' COMMENT '通知类型',
  `status` enum('unread','read') NOT NULL DEFAULT 'unread' COMMENT '通知状态',
  `avatar` varchar(255) DEFAULT NULL COMMENT '头像URL',
  `related_id` int DEFAULT NULL COMMENT '关联数据ID',
  `related_type` varchar(50) DEFAULT NULL COMMENT '关联数据类型',
  `related_url` varchar(500) DEFAULT NULL COMMENT '关联URL',
  `priority` int NOT NULL DEFAULT '3' COMMENT '优先级(1-5, 1为最高)',
  `expires_at` datetime DEFAULT NULL COMMENT '过期时间',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_receiver` (`receiver_id`, `receiver_type`),
  KEY `idx_status` (`status`),
  KEY `idx_type` (`type`),
  KEY `idx_created_at` (`created_at`),
  KEY `idx_expires_at` (`expires_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统通知表';

-- 插入示例数据
INSERT INTO `sys_notification` (
  `receiver_id`, `receiver_type`, `sender_id`, `sender_name`, `title`, `message`, `type`, `status`, `avatar`, `priority`, `created_at`
) VALUES
(1, 'admin', NULL, NULL, '系统备份完成通知', '系统已自动完成数据备份，备份文件大小 2.3GB，耗时 15 分钟', 'system', 'read', 'https://api.dicebear.com/7.x/avataaars/svg?seed=system', 3, NOW() - INTERVAL 3 HOUR),
(1, 'admin', 2, '朱偏右', '朱偏右 回复了你的消息', '关于项目进度的问题，我已经在文档中更新了详细说明，请查看最新版本', 'message', 'unread', 'https://api.dicebear.com/7.x/avataaars/svg?seed=zhupianyou', 3, NOW() - INTERVAL 45 MINUTE),
(1, 'admin', 3, '曲丽丽', '曲丽丽 评论了你的设计稿', '这个功能设计得很棒！建议在用户引导部分增加一些操作示例', 'comment', 'unread', 'https://api.dicebear.com/7.x/avataaars/svg?seed=qulili', 3, NOW() - INTERVAL 2 HOUR),
(1, 'admin', NULL, NULL, '会议提醒', '月度技术分享会将在明天下午 2:00 举行，请提前准备演示材料', 'reminder', 'unread', 'https://api.dicebear.com/7.x/avataaars/svg?seed=reminder', 2, NOW() - INTERVAL 1 DAY),
(1, 'admin', NULL, NULL, '请假申请已审批通过', '你的请假申请（2025-11-18 至 2025-11-20）已通过审批', 'approval', 'unread', 'https://api.dicebear.com/7.x/avataaars/svg?seed=approval', 3, NOW() - INTERVAL 6 HOUR),
(1, 'admin', NULL, NULL, '安全警告', '检测到来自 IP 192.168.1.100 的异常登录尝试，系统已自动阻止', 'security', 'read', 'https://api.dicebear.com/7.x/avataaars/svg?seed=security', 1, NOW() - INTERVAL 2 DAY),
(1, 'admin', NULL, NULL, '系统更新通知', '新版本 v2.1.0 已发布，包含性能优化和 bug 修复，建议尽快更新', 'update', 'read', 'https://api.dicebear.com/7.x/avataaars/svg?seed=update', 2, NOW() - INTERVAL 3 DAY),
(1, 'admin', NULL, NULL, '任务到期提醒', '项目需求文档评审任务即将到期，请及时完成评审工作', 'task', 'unread', 'https://api.dicebear.com/7.x/avataaars/svg?seed=task', 2, NOW() - INTERVAL 12 HOUR);
