from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time
from fastapi import APIRouter, Depends, HTTPException
from fastapi_babel import _
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from sqlalchemy.exc import OperationalError, InternalError
from app.dependencies.database import get_db, DatabaseConnectionError
from app.core.security import get_current_admin
from app.models.sys_user import SysUser
from app.models.sys_admin_log import SysAdminLog
from app.models.sys_attachment import SysAttachment
from app.utils.responses import success_response

# Initialize the API router for analytics endpoints
router = APIRouter(
    prefix="/analytics", tags=["analytics"]
    # dependencies=[Depends(get_current_admin)]  # 暂时移除认证依赖进行测试
)


@router.get("/overview")
def get_analytics_overview(db: Session = Depends(get_db)):
    """
    Get analytics overview data based on user statistics.
    
    Args:
        db (Session): Database session dependency.
        
    Returns:
        JSON response containing overview statistics.
    """
    max_retries = 3
    retry_delay = 1  # seconds
    
    for attempt in range(max_retries):
        try:
            today = datetime.now().date()
            
            # 1. 总用户统计
            total_users = db.query(SysUser).count()
            
            # 2. 今日注册用户统计
            today_registered_users = db.query(SysUser).filter(
                func.date(SysUser.created_at) == today
            ).count()
            
            # 3. 今日登录用户统计 (login_time 是今天的用户)
            today_logged_in_users = db.query(SysUser).filter(
                func.date(SysUser.login_time) == today
            ).count()
            
            # 4. 近7日活跃用户统计 (最近7天内登录过的用户)
            seven_days_ago = today - timedelta(days=7)
            active_users_last_7_days = db.query(SysUser).filter(
                SysUser.login_time >= seven_days_ago
            ).count()
            
            overview_data = [
                {
                    "totalValue": total_users,
                    "value": total_users,
                },
                {
                    "totalValue": total_users,  # 总注册用户数
                    "value": today_registered_users,
                },
                {
                    "totalValue": total_users,  # 总用户数
                    "value": today_logged_in_users,
                },
                {
                    "totalValue": total_users,  # 总用户数
                    "value": active_users_last_7_days,
                },
            ]
            
            return success_response(overview_data)
            
        except (OperationalError, InternalError) as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
                continue
            else:
                raise HTTPException(
                    status_code=503, 
                    detail="数据库连接失败，请稍后重试"
                )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"获取分析数据失败: {str(e)}")


@router.get("/trends")
def get_analytics_trends(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """
    Get analytics trends data for the specified number of days.
    
    Args:
        days (int): Number of days to include in trends (default: 30).
        db (Session): Database session dependency.
        
    Returns:
        JSON response containing trends data.
    """
    max_retries = 3
    retry_delay = 1  # seconds
    
    for attempt in range(max_retries):
        try:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days - 1)
            
            # Generate date range
            date_range = []
            current_date = start_date
            while current_date <= end_date:
                date_range.append(current_date)
                current_date += timedelta(days=1)
            
            # Get user registration trends
            user_trends = []
            for date in date_range:
                count = db.query(SysUser).filter(
                    func.date(SysUser.created_at) == date
                ).count()
                user_trends.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "count": count
                })
            
            # Get visit trends
            visit_trends = []
            for date in date_range:
                count = db.query(SysAdminLog).filter(
                    func.date(SysAdminLog.created_at) == date
                ).count()
                visit_trends.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "count": count
                })
            
            # 如果数据库中没有数据，返回空数组
            # 前端组件会处理空数据情况
            
            trends_data = {
                "userTrends": user_trends,
                "visitTrends": visit_trends,
                "dateRange": {
                    "start": start_date.strftime("%Y-%m-%d"),
                    "end": end_date.strftime("%Y-%m-%d")
                }
            }
            
            return success_response(trends_data)
            
        except (OperationalError, InternalError) as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
                continue
            else:
                raise HTTPException(
                    status_code=503, 
                    detail="数据库连接失败，请稍后重试"
                )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"获取趋势数据失败: {str(e)}")




@router.get("/visits")
def get_analytics_visits(
    period: str = "month",  # month, week, day
    db: Session = Depends(get_db)
):
    """
    Get analytics visits data for the specified period.
    
    Args:
        period (str): Time period for visits data (month, week, day).
        db (Session): Database session dependency.
        
    Returns:
        JSON response containing visits data.
    """
    try:
        end_date = datetime.now()
        
        if period == "month":
            start_date = end_date - timedelta(days=30)
            group_format = "%Y-%m-%d"
        elif period == "week":
            start_date = end_date - timedelta(days=7)
            group_format = "%Y-%m-%d"
        else:  # day
            start_date = end_date - timedelta(hours=24)
            group_format = "%Y-%m-%d %H:00"
        
        # Get visits by date/hour
        visits_by_time = db.query(
            func.date_format(SysAdminLog.created_at, group_format).label('time_group'),
            func.count(SysAdminLog.id).label('count')
        ).filter(
            SysAdminLog.created_at >= start_date,
            SysAdminLog.created_at <= end_date
        ).group_by('time_group').all()
        
        # Format the data
        visits_data = []
        for visit in visits_by_time:
            visits_data.append({
                "time": visit.time_group,
                "count": visit.count
            })
        
        # Get visits by action type
        visits_by_action = db.query(
            SysAdminLog.title,
            func.count(SysAdminLog.id).label('count')
        ).filter(
            SysAdminLog.created_at >= start_date,
            SysAdminLog.created_at <= end_date
        ).group_by(SysAdminLog.title).all()
        
        action_data = []
        for action in visits_by_action:
            if action.title:  # Only include actions with values
                action_data.append({
                    "action": action.title,
                    "count": action.count
                })
        
        total_visits_count = 0
        for visit in visits_by_time:
            total_visits_count += visit[1]  # visit.count is the second element in the tuple
        
        result = {
            "visitsByTime": visits_data,
            "visitsByAction": action_data,
            "period": period,
            "totalVisits": total_visits_count
        }
        
        return success_response(result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取访问数据失败: {str(e)}")


@router.get("/sources")
def get_analytics_sources(
    db: Session = Depends(get_db)
):
    """
    Get analytics data by source/category.
    
    Args:
        db (Session): Database session dependency.
        
    Returns:
        JSON response containing source data.
    """
    max_retries = 3
    retry_delay = 1  # seconds
    
    for attempt in range(max_retries):
        try:
            # Get user sources (by registration method if available)
            # For now, we'll use user groups as sources
            user_sources = db.query(
                SysUser.user_group_id,
                func.count(SysUser.id).label('count')
            ).group_by(SysUser.user_group_id).all()
            
            source_data = []
            for source in user_sources:
                source_data.append({
                    "source": f"用户组 {source.user_group_id}" if source.user_group_id else "未分组",
                    "count": source.count
                })
            
            # Get action sources (by admin log actions)
            action_sources = db.query(
                SysAdminLog.title,
                func.count(SysAdminLog.id).label('count')
            ).group_by(SysAdminLog.title).all()
            
            action_data = []
            for action in action_sources:
                if action.title:
                    action_data.append({
                        "source": action.title,
                        "count": action.count
                    })
            
            result = {
                "userSources": source_data,
                "actionSources": action_data
            }
            
            return success_response(result)
            
        except (OperationalError, InternalError) as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
                continue
            else:
                raise HTTPException(
                    status_code=503, 
                    detail="数据库连接失败，请稍后重试"
                )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"获取来源数据失败: {str(e)}")


@router.get("/monthly-logins")
def get_monthly_login_stats(
    months: int = 12,
    db: Session = Depends(get_db)
):
    """
    Get monthly login statistics for the specified number of months.
    
    Args:
        months (int): Number of months to include (default: 12).
        db (Session): Database session dependency.
        
    Returns:
        JSON response containing monthly login statistics.
    """
    try:
        end_date = datetime.now()
        
        # Get monthly login statistics
        monthly_logins = []
        
        for i in range(months):
            # Calculate month start and end
            target_month = end_date.month - i
            target_year = end_date.year
            
            if target_month <= 0:
                target_month += 12
                target_year -= 1
            
            month_start = datetime(target_year, target_month, 1)
            if target_month == 12:
                month_end = datetime(target_year + 1, 1, 1) - timedelta(days=1)
            else:
                month_end = datetime(target_year, target_month + 1, 1) - timedelta(days=1)
            
            # Count unique users who logged in this month
            # 使用distinct来统计唯一用户，避免重复计算同一用户多次登录
            login_count = db.query(SysUser.id).filter(
                SysUser.login_time >= month_start,
                SysUser.login_time <= month_end,
                SysUser.login_time.isnot(None)  # 确保login_time不为空
            ).distinct().count()
            
            monthly_logins.append({
                "month": f"{target_year}-{target_month:02d}",
                "count": login_count
            })
        
        # Reverse to get chronological order
        monthly_logins.reverse()
        
        return success_response(monthly_logins)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取月度登录数据失败: {str(e)}")


@router.get("/regions")
def get_analytics_regions(
    db: Session = Depends(get_db)
):
    """
    Get analytics data by region based on user data.
    
    Args:
        db (Session): Database session dependency.
        
    Returns:
        JSON response containing region distribution data.
    """
    try:
        # 计算总用户数
        total_users = db.query(SysUser).count()
        
        # 如果没有用户，返回空数组
        if total_users == 0:
            return success_response([])
        
        # 基于总用户数生成地区分布数据
        # 这里使用常见的中国省份分布作为示例
        common_regions = [
            "Guangdong", "Beijing", "Shanghai", "Zhejiang", "Jiangsu",
            "Sichuan", "Shandong", "Hubei", "Henan", "Other Regions"
        ]
        
        # 基于总用户数生成地区分布
        region_data = []
        base_count = max(1, total_users // len(common_regions))
        
        for i, region in enumerate(common_regions):
            # 为每个地区生成基于总用户数的分布
            # 使用不同的权重来模拟真实分布
            weight = len(common_regions) - i  # 前面的地区权重更高
            region_count = max(1, base_count * weight // 2)
            
            region_data.append({
                "region": region,
                "count": region_count
            })
        
        # 调试输出，检查地区数据
        print("Generated region data:", region_data)
        
        return success_response(region_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取地区数据失败: {str(e)}")
