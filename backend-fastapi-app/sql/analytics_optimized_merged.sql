-- 分析数据表合并优化方案
-- 将原有的3个统计表合并为1个统一的分析汇总表

-- 删除原有的3个统计表（如果存在）
DROP TABLE IF EXISTS analytics_daily_summary;
DROP TABLE IF EXISTS analytics_monthly_summary;
DROP TABLE IF EXISTS analytics_user_regions;

-- 创建统一的分析汇总表
CREATE TABLE IF NOT EXISTS analytics_summary (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    
    -- 时间维度标识
    summary_type ENUM('daily', 'monthly', 'regional') NOT NULL COMMENT 'Summary type: daily-daily summary, monthly-monthly summary, regional-regional summary',
    
    -- 时间维度字段（根据类型使用不同的字段）
    summary_date DATE NULL COMMENT 'Summary date (for daily summary)',
    summary_year INT NULL COMMENT 'Summary year (for monthly summary)',
    summary_month INT NULL COMMENT 'Summary month (for monthly summary)',
    region_name VARCHAR(100) NULL COMMENT 'Region name (for regional summary)',
    
    -- 核心统计指标
    total_users INT DEFAULT 0 COMMENT 'Total users',
    new_users INT DEFAULT 0 COMMENT 'New users',
    active_users INT DEFAULT 0 COMMENT 'Active users',
    total_logins INT DEFAULT 0 COMMENT 'Total logins',
    total_visits INT DEFAULT 0 COMMENT 'Total visits',
    
    -- 用户组分布（JSON格式存储，避免多表关联）
    user_group_distribution JSON NULL COMMENT 'User group distribution statistics',
    
    -- 操作类型分布（JSON格式存储）
    action_distribution JSON NULL COMMENT 'Action type distribution statistics',
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- 复合唯一约束，确保数据不重复
    UNIQUE KEY unique_daily_summary (summary_type, summary_date),
    UNIQUE KEY unique_monthly_summary (summary_type, summary_year, summary_month),
    UNIQUE KEY unique_regional_summary (summary_type, region_name),
    
    -- 索引优化
    INDEX idx_summary_type_date (summary_type, summary_date),
    INDEX idx_summary_type_year_month (summary_type, summary_year, summary_month),
    INDEX idx_summary_type_region (summary_type, region_name),
    INDEX idx_created_at (created_at),
    INDEX idx_updated_at (updated_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Unified analytics summary table';

-- 创建数据填充存储过程
DELIMITER //

CREATE PROCEDURE IF NOT EXISTS populate_analytics_summary()
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE current_date_val DATE;
    DECLARE current_year_val INT;
    DECLARE current_month_val INT;
    DECLARE region_val VARCHAR(100);
    
    -- 游标声明
    DECLARE date_cursor CURSOR FOR 
        SELECT DISTINCT DATE(created_at) FROM sys_user 
        WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
        UNION
        SELECT DISTINCT DATE(created_at) FROM sys_admin_log 
        WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL 30 DAY);
    
    DECLARE month_cursor CURSOR FOR 
        SELECT DISTINCT YEAR(created_at), MONTH(created_at) 
        FROM sys_user 
        WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
        UNION
        SELECT DISTINCT YEAR(created_at), MONTH(created_at) 
        FROM sys_admin_log 
        WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH);
    
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
    
    -- 填充日汇总数据
    OPEN date_cursor;
    date_loop: LOOP
        FETCH date_cursor INTO current_date_val;
        IF done THEN
            LEAVE date_loop;
        END IF;
        
        -- 插入或更新日汇总数据
        INSERT INTO analytics_summary (
            summary_type, summary_date, 
            total_users, new_users, active_users, total_logins, total_visits,
            user_group_distribution, action_distribution
        )
        SELECT 
            'daily' as summary_type,
            current_date_val as summary_date,
            -- 总用户数（截至该日期）
            (SELECT COUNT(*) FROM sys_user WHERE DATE(created_at) <= current_date_val) as total_users,
            -- 新增用户数（该日期）
            (SELECT COUNT(*) FROM sys_user WHERE DATE(created_at) = current_date_val) as new_users,
            -- 活跃用户数（该日期有登录）
            (SELECT COUNT(DISTINCT id) FROM sys_user WHERE DATE(login_time) = current_date_val AND login_time IS NOT NULL) as active_users,
            -- 总登录次数（该日期）
            (SELECT COUNT(*) FROM sys_user WHERE DATE(login_time) = current_date_val AND login_time IS NOT NULL) as total_logins,
            -- 总访问次数（该日期）
            (SELECT COUNT(*) FROM sys_admin_log WHERE DATE(created_at) = current_date_val) as total_visits,
            -- 用户组分布
            (SELECT JSON_OBJECTAGG(COALESCE(user_group_id, 0), user_count)
             FROM (SELECT user_group_id, COUNT(*) as user_count 
                   FROM sys_user 
                   WHERE DATE(created_at) <= current_date_val
                   GROUP BY user_group_id) as user_groups) as user_group_distribution,
            -- 操作类型分布
            (SELECT JSON_OBJECTAGG(title, action_count)
             FROM (SELECT title, COUNT(*) as action_count 
                   FROM sys_admin_log 
                   WHERE DATE(created_at) = current_date_val
                   GROUP BY title) as user_actions) as action_distribution
        ON DUPLICATE KEY UPDATE
            total_users = VALUES(total_users),
            new_users = VALUES(new_users),
            active_users = VALUES(active_users),
            total_logins = VALUES(total_logins),
            total_visits = VALUES(total_visits),
            user_group_distribution = VALUES(user_group_distribution),
            action_distribution = VALUES(action_distribution),
            updated_at = CURRENT_TIMESTAMP;
        
    END LOOP date_loop;
    CLOSE date_cursor;
    
    -- 重置完成标志
    SET done = FALSE;
    
    -- 填充月汇总数据
    OPEN month_cursor;
    month_loop: LOOP
        FETCH month_cursor INTO current_year_val, current_month_val;
        IF done THEN
            LEAVE month_loop;
        END IF;
        
        -- 插入或更新月汇总数据
        INSERT INTO analytics_summary (
            summary_type, summary_year, summary_month,
            total_users, new_users, active_users, total_logins, total_visits,
            user_group_distribution, action_distribution
        )
        SELECT 
            'monthly' as summary_type,
            current_year_val as summary_year,
            current_month_val as summary_month,
            -- 总用户数（截至该月末）
            (SELECT COUNT(*) FROM sys_user 
             WHERE YEAR(created_at) < current_year_val 
                OR (YEAR(created_at) = current_year_val AND MONTH(created_at) <= current_month_val)) as total_users,
            -- 新增用户数（该月）
            (SELECT COUNT(*) FROM sys_user 
             WHERE YEAR(created_at) = current_year_val AND MONTH(created_at) = current_month_val) as new_users,
            -- 活跃用户数（该月有登录）
            (SELECT COUNT(DISTINCT id) FROM sys_user 
             WHERE YEAR(login_time) = current_year_val AND MONTH(login_time) = current_month_val AND login_time IS NOT NULL) as active_users,
            -- 总登录次数（该月）
            (SELECT COUNT(*) FROM sys_user 
             WHERE YEAR(login_time) = current_year_val AND MONTH(login_time) = current_month_val AND login_time IS NOT NULL) as total_logins,
            -- 总访问次数（该月）
            (SELECT COUNT(*) FROM sys_admin_log 
             WHERE YEAR(created_at) = current_year_val AND MONTH(created_at) = current_month_val) as total_visits,
            -- 用户组分布
            (SELECT JSON_OBJECTAGG(COALESCE(user_group_id, 0), user_count)
             FROM (SELECT user_group_id, COUNT(*) as user_count 
                   FROM sys_user 
                   WHERE YEAR(created_at) < current_year_val 
                      OR (YEAR(created_at) = current_year_val AND MONTH(created_at) <= current_month_val)
                   GROUP BY user_group_id) as monthly_user_groups) as user_group_distribution,
            -- 操作类型分布
            (SELECT JSON_OBJECTAGG(title, action_count)
             FROM (SELECT title, COUNT(*) as action_count 
                   FROM sys_admin_log 
                   WHERE YEAR(created_at) = current_year_val AND MONTH(created_at) = current_month_val
                   GROUP BY title) as monthly_actions) as action_distribution
        ON DUPLICATE KEY UPDATE
            total_users = VALUES(total_users),
            new_users = VALUES(new_users),
            active_users = VALUES(active_users),
            total_logins = VALUES(total_logins),
            total_visits = VALUES(total_visits),
            user_group_distribution = VALUES(user_group_distribution),
            action_distribution = VALUES(action_distribution),
            updated_at = CURRENT_TIMESTAMP;
        
    END LOOP month_loop;
    CLOSE month_cursor;
    
END //

DELIMITER ;

-- 创建定时任务事件（每天凌晨执行）
CREATE EVENT IF NOT EXISTS analytics_summary_daily_update
ON SCHEDULE EVERY 1 DAY
STARTS TIMESTAMP(CURRENT_DATE, '00:05:00')
DO
CALL populate_analytics_summary();

-- 启用事件调度器（如果未启用）
SET GLOBAL event_scheduler = ON;

-- 创建优化的API查询视图
CREATE OR REPLACE VIEW analytics_daily_view AS
SELECT 
    summary_date as date,
    total_users,
    new_users,
    active_users,
    total_logins,
    total_visits,
    user_group_distribution,
    action_distribution
FROM analytics_summary
WHERE summary_type = 'daily'
ORDER BY summary_date DESC;

CREATE OR REPLACE VIEW analytics_monthly_view AS
SELECT 
    CONCAT(summary_year, '-', LPAD(summary_month, 2, '0')) as month,
    total_users,
    new_users,
    active_users,
    total_logins,
    total_visits,
    user_group_distribution,
    action_distribution
FROM analytics_summary
WHERE summary_type = 'monthly'
ORDER BY summary_year DESC, summary_month DESC;

-- 性能优化建议：
-- 1. 建议在业务低峰期执行此脚本
-- 2. 定期清理历史数据（保留最近2年的数据）
-- 3. 监控存储空间使用情况
-- 4. 根据实际业务需求调整汇总频率

-- 数据清理策略示例
-- DELETE FROM analytics_summary 
-- WHERE summary_type = 'daily' AND summary_date < DATE_SUB(CURDATE(), INTERVAL 2 YEAR);

-- 使用说明：
-- 1. 执行此脚本前请备份现有数据
-- 2. 执行后原有的3个统计表将被删除
-- 3. 新的统一表将自动开始收集数据
-- 4. API代码需要相应更新以使用新的表结构
