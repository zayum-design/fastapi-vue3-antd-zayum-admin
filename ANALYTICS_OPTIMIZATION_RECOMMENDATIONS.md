# Analytics API 性能优化建议

## 当前性能问题分析

通过分析 `backend-fastapi-app/app/api/admin/analytics.py`，发现以下主要性能瓶颈：

### 1. 数据库查询问题
- **N+1 查询问题**：在趋势数据查询中，对每个日期都执行单独的 COUNT 查询
- **全表扫描**：大量使用 `COUNT(*)` 查询，没有利用索引
- **重复查询**：多个端点查询相同的基础数据

### 2. 缺乏缓存机制
- 所有统计查询都是实时执行
- 频繁访问的数据没有缓存
- 高并发场景下数据库压力大

### 3. 同步阻塞操作
- 所有数据库操作都是同步的
- 大数据量查询会阻塞其他请求

## 优化方案

### 1. 缓存策略优化

#### 1.1 实现 Redis 缓存层

```python
# 新增缓存工具类
import json
from datetime import datetime, timedelta
from typing import Any, Optional
import redis.asyncio as redis
from app.core.cache import get_redis

class AnalyticsCache:
    def __init__(self):
        self.redis_client = None
    
    async def get_client(self):
        if self.redis_client is None:
            self.redis_client = await get_redis()
        return self.redis_client
    
    async def get(self, key: str) -> Optional[Any]:
        client = await self.get_client()
        data = await client.get(key)
        return json.loads(data) if data else None
    
    async def set(self, key: str, value: Any, expire: int = 300):
        client = await self.get_client()
        await client.setex(key, expire, json.dumps(value))
    
    async def delete(self, key: str):
        client = await self.get_client()
        await client.delete(key)

analytics_cache = AnalyticsCache()
```

#### 1.2 缓存键设计
```python
def get_cache_key(endpoint: str, params: dict) -> str:
    """生成缓存键"""
    param_str = "_".join(f"{k}_{v}" for k, v in sorted(params.items()))
    return f"analytics:{endpoint}:{param_str}"
```

### 2. 数据库查询优化

#### 2.1 使用批量查询替代循环查询

**优化前（趋势数据查询）：**
```python
# 低效：每个日期执行一次查询
user_trends = []
for date in date_range:
    count = db.query(SysUser).filter(
        func.date(SysUser.created_at) == date
    ).count()
    user_trends.append({
        "date": date.strftime("%Y-%m-%d"),
        "count": count
    })
```

**优化后：**
```python
# 高效：单次查询获取所有数据
user_trends_query = db.query(
    func.date(SysUser.created_at).label('date'),
    func.count(SysUser.id).label('count')
).filter(
    SysUser.created_at >= start_date,
    SysUser.created_at <= end_date
).group_by(func.date(SysUser.created_at)).all()

user_trends = [
    {
        "date": row.date.strftime("%Y-%m-%d"),
        "count": row.count
    }
    for row in user_trends_query
]
```

#### 2.2 添加数据库索引
```sql
-- 为常用查询字段添加索引
CREATE INDEX idx_sys_user_created_at ON sys_user(created_at);
CREATE INDEX idx_sys_user_login_time ON sys_user(login_time);
CREATE INDEX idx_sys_admin_log_created_at ON sys_admin_log(created_at);
CREATE INDEX idx_sys_admin_log_title ON sys_admin_log(title);
```

### 3. 异步处理优化

#### 3.1 将同步端点改为异步

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.database import get_async_db

@router.get("/overview")
async def get_analytics_overview(db: AsyncSession = Depends(get_async_db)):
    """异步获取分析概览数据"""
    cache_key = get_cache_key("overview", {})
    
    # 尝试从缓存获取
    cached_data = await analytics_cache.get(cache_key)
    if cached_data:
        return success_response(cached_data)
    
    # 缓存未命中，查询数据库
    try:
        today = datetime.now().date()
        
        # 使用异步查询
        total_users = await db.scalar(
            select(func.count(SysUser.id))
        )
        
        today_registered_users = await db.scalar(
            select(func.count(SysUser.id)).where(
                func.date(SysUser.created_at) == today
            )
        )
        
        # ... 其他查询
        
        overview_data = [...]  # 构建数据
        
        # 缓存结果（5分钟过期）
        await analytics_cache.set(cache_key, overview_data, 300)
        
        return success_response(overview_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取分析数据失败: {str(e)}")
```

### 4. 数据聚合优化

#### 4.1 创建统计汇总表
```sql
-- 创建每日统计汇总表
CREATE TABLE analytics_daily_summary (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    summary_date DATE NOT NULL,
    total_users INT DEFAULT 0,
    new_users INT DEFAULT 0,
    active_users INT DEFAULT 0,
    total_visits INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_date (summary_date)
);
```

#### 4.2 定时任务更新汇总数据
```python
# 新增定时任务模块
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

async def update_daily_summary():
    """每日更新统计汇总数据"""
    yesterday = datetime.now().date() - timedelta(days=1)
    
    # 查询昨日数据并更新汇总表
    # 这里可以批量计算所有统计数据
    
    # 清除相关缓存
    await analytics_cache.delete("analytics:overview")
    await analytics_cache.delete("analytics:trends:*")
```

### 5. 分页和限制优化

#### 5.1 为大数据量查询添加限制
```python
@router.get("/trends")
async def get_analytics_trends(
    days: int = Query(30, ge=1, le=365),  # 限制最大365天
    db: AsyncSession = Depends(get_async_db)
):
    """获取趋势数据，限制查询天数"""
    if days > 90:  # 超过90天使用汇总数据
        return await get_aggregated_trends(days, db)
    
    # ... 原有逻辑
```

## 具体优化实现

### 优化后的 analytics.py 示例

```python
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from sqlalchemy.exc import OperationalError, InternalError

from app.dependencies.database import get_async_db
from app.core.security import get_current_admin
from app.models.sys_user import SysUser
from app.models.sys_admin_log import SysAdminLog
from app.utils.responses import success_response
from app.core.cache import analytics_cache, get_cache_key

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/overview")
async def get_analytics_overview(db: AsyncSession = Depends(get_async_db)):
    """获取分析概览数据（带缓存）"""
    cache_key = get_cache_key("overview", {})
    
    # 尝试从缓存获取
    cached_data = await analytics_cache.get(cache_key)
    if cached_data:
        return success_response(cached_data)
    
    try:
        today = datetime.now().date()
        seven_days_ago = today - timedelta(days=7)
        
        # 批量查询所有统计数据
        queries = await asyncio.gather(
            db.scalar(select(func.count(SysUser.id))),  # 总用户数
            db.scalar(select(func.count(SysUser.id)).where(
                func.date(SysUser.created_at) == today
            )),  # 今日注册用户
            db.scalar(select(func.count(SysUser.id)).where(
                func.date(SysUser.login_time) == today
            )),  # 今日登录用户
            db.scalar(select(func.count(SysUser.id)).where(
                SysUser.login_time >= seven_days_ago
            )),  # 近7日活跃用户
        )
        
        total_users, today_registered, today_logged_in, active_7_days = queries
        
        overview_data = [
            {"totalValue": total_users, "value": total_users},
            {"totalValue": total_users, "value": today_registered},
            {"totalValue": total_users, "value": today_logged_in},
            {"totalValue": total_users, "value": active_7_days},
        ]
        
        # 缓存5分钟
        await analytics_cache.set(cache_key, overview_data, 300)
        
        return success_response(overview_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取分析数据失败: {str(e)}")

@router.get("/trends")
async def get_analytics_trends(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_async_db)
):
    """获取趋势数据（优化批量查询）"""
    cache_key = get_cache_key("trends", {"days": days})
    
    cached_data = await analytics_cache.get(cache_key)
    if cached_data:
        return success_response(cached_data)
    
    try:
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days - 1)
        
        # 批量查询用户注册趋势
        user_trends_query = await db.execute(
            select(
                func.date(SysUser.created_at).label('date'),
                func.count(SysUser.id).label('count')
            ).where(
                SysUser.created_at >= start_date,
                SysUser.created_at <= end_date
            ).group_by(func.date(SysUser.created_at))
        )
        user_trends = [
            {"date": row.date.strftime("%Y-%m-%d"), "count": row.count}
            for row in user_trends_query.all()
        ]
        
        # 批量查询访问趋势
        visit_trends_query = await db.execute(
            select(
                func.date(SysAdminLog.created_at).label('date'),
                func.count(SysAdminLog.id).label('count')
            ).where(
                SysAdminLog.created_at >= start_date,
                SysAdminLog.created_at <= end_date
            ).group_by(func.date(SysAdminLog.created_at))
        )
        visit_trends = [
            {"date": row.date.strftime("%Y-%m-%d"), "count": row.count}
            for row in visit_trends_query.all()
        ]
        
        trends_data = {
            "userTrends": user_trends,
            "visitTrends": visit_trends,
            "dateRange": {
                "start": start_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d")
            }
        }
        
        # 根据天数设置不同的缓存时间
        cache_time = 300 if days <= 7 else 1800  # 7天内5分钟，超过7天30分钟
        await analytics_cache.set(cache_key, trends_data, cache_time)
        
        return success_response(trends_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取趋势数据失败: {str(e)}")
```

## 性能提升预期

通过上述优化，预期可以获得以下性能提升：

1. **数据库负载降低 70-80%**：通过缓存和批量查询
2. **响应时间提升 60-90%**：缓存命中时响应时间从几百毫秒降低到几毫秒
3. **并发处理能力提升**：异步处理避免阻塞
4. **可扩展性增强**：支持更高并发访问

## 实施步骤

1. **第一阶段**：实现缓存层和批量查询优化
2. **第二阶段**：迁移到异步数据库操作
3. **第三阶段**：创建统计汇总表和定时任务
4. **第四阶段**：监控和性能调优

建议按阶段逐步实施，每个阶段完成后进行性能测试验证效果。
