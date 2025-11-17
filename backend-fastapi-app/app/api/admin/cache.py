"""
缓存管理API
提供缓存清理功能
"""
from typing import Dict
from fastapi import APIRouter, Depends, HTTPException

from app.core.security import get_current_admin
from app.utils.responses import success_response
from app.core.cache import delete_cached_pattern_sync
from app.utils.log_utils import logger


def clear_analytics_cache_sync():
    """
    清除所有分析数据缓存（同步版本）
    在数据更新后调用此函数
    """
    try:
        delete_cached_pattern_sync("analytics:*")
        logger.info("AnalyticsCache: Cleared all analytics cache synchronously")
    except Exception as e:
        logger.error(f"AnalyticsCache: Failed to clear cache synchronously: {e}")


# Initialize the API router for cache endpoints
router = APIRouter(
    prefix="/cache", 
    tags=["cache"],
    dependencies=[Depends(get_current_admin)] 
)


@router.post("/clear")
def clear_analytics_cache_endpoint():
    """
    手动清除分析数据缓存
    用于开发调试或数据更新后强制刷新缓存
    """
    try:
        clear_analytics_cache_sync()
        return success_response({"message": "分析数据缓存已清除"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清除缓存失败: {str(e)}")
