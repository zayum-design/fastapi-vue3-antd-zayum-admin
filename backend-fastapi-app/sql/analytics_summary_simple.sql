-- Simplified Analytics Summary Table Creation
-- Alternative to the complex stored procedure version

-- Drop existing analytics tables if they exist
DROP TABLE IF EXISTS analytics_daily_summary;
DROP TABLE IF EXISTS analytics_monthly_summary;
DROP TABLE IF EXISTS analytics_user_regions;

-- Create unified analytics summary table
CREATE TABLE IF NOT EXISTS analytics_summary (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    
    -- Summary type dimension
    summary_type ENUM('daily', 'monthly', 'regional') NOT NULL COMMENT 'Summary type: daily-daily summary, monthly-monthly summary, regional-regional summary',
    
    -- Time dimension fields (used based on summary_type)
    summary_date DATE NULL COMMENT 'Summary date (for daily summary)',
    summary_year INT NULL COMMENT 'Summary year (for monthly summary)',
    summary_month INT NULL COMMENT 'Summary month (for monthly summary)',
    region_name VARCHAR(100) NULL COMMENT 'Region name (for regional summary)',
    
    -- Core statistics metrics
    total_users INT DEFAULT 0 COMMENT 'Total users',
    new_users INT DEFAULT 0 COMMENT 'New users',
    active_users INT DEFAULT 0 COMMENT 'Active users',
    total_logins INT DEFAULT 0 COMMENT 'Total logins',
    total_visits INT DEFAULT 0 COMMENT 'Total visits',
    
    -- Distribution data in JSON format
    user_group_distribution JSON NULL COMMENT 'User group distribution statistics',
    action_distribution JSON NULL COMMENT 'Action type distribution statistics',
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Composite unique constraints
    UNIQUE KEY unique_daily_summary (summary_type, summary_date),
    UNIQUE KEY unique_monthly_summary (summary_type, summary_year, summary_month),
    UNIQUE KEY unique_regional_summary (summary_type, region_name),
    
    -- Index optimization
    INDEX idx_summary_type_date (summary_type, summary_date),
    INDEX idx_summary_type_year_month (summary_type, summary_year, summary_month),
    INDEX idx_summary_type_region (summary_type, region_name),
    INDEX idx_created_at (created_at),
    INDEX idx_updated_at (updated_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Unified analytics summary table';

-- Create simplified views for API queries
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

-- Insert sample data for testing
INSERT INTO analytics_summary (
    summary_type, summary_date, 
    total_users, new_users, active_users, total_logins, total_visits,
    user_group_distribution, action_distribution
) VALUES 
('daily', CURDATE() - INTERVAL 1 DAY, 1000, 50, 300, 450, 1200, 
 '{"1": 400, "2": 350, "3": 250}', 
 '{"login": 450, "view": 500, "create": 250}'),
 
('daily', CURDATE(), 1050, 50, 320, 480, 1300, 
 '{"1": 420, "2": 360, "3": 270}', 
 '{"login": 480, "view": 550, "create": 270}'),
 
('monthly', YEAR(CURDATE()), MONTH(CURDATE()), 1050, 150, 950, 4500, 12500, 
 '{"1": 420, "2": 360, "3": 270}', 
 '{"login": 4500, "view": 5500, "create": 2500}');

-- Performance optimization recommendations:
-- 1. Run this script during low-traffic hours
-- 2. Monitor storage usage regularly
-- 3. Clean up old data periodically (keep last 2 years)
-- 4. Adjust summary frequency based on business needs

-- Example data cleanup strategy:
-- DELETE FROM analytics_summary 
-- WHERE summary_type = 'daily' AND summary_date < DATE_SUB(CURDATE(), INTERVAL 2 YEAR);

-- Usage instructions:
-- 1. Backup existing data before executing this script
-- 2. The original 3 analytics tables will be dropped
-- 3. The new unified table will be created with sample data
-- 4. API code should be updated to use the new table structure
