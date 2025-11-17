"""
通知管理API
提供通知相关的功能
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_admin
from app.dependencies.database import get_db
from app.crud.sys_notification import crud_sys_notification
from app.models.sys_notification import SysNotification
from app.utils.responses import success_response
from app.utils.log_utils import logger


# Initialize the API router for notifications endpoints
router = APIRouter(
    prefix="/notifications", 
    tags=["notifications"],
    dependencies=[Depends(get_current_admin)] 
)


@router.get("/list")
def get_notifications_list(
    page: int = 1,
    per_page: int = 10,
    search: Optional[str] = None,
    orderby: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    获取通知列表
    从数据库获取真实通知数据
    """
    try:
        # 确保分页参数有效
        page = max(1, page)
        per_page = max(1, min(per_page, 100))
        
        # 获取通知数据
        notifications = crud_sys_notification.get_multi(
            db, page=page, per_page=per_page, search=search, orderby=orderby
        )
        total = crud_sys_notification.get_total(db, search=search)
        
        # 转换数据格式以匹配前端期望的格式
        formatted_notifications = []
        for notification in notifications:
            formatted_notifications.append({
                "id": notification.id,
                "avatar": notification.avatar,
                "date": notification.created_at.strftime("%Y-%m-%d %H:%M:%S") if notification.created_at else "",
                "isRead": notification.status == "read",
                "message": notification.message,
                "title": notification.title,
                "type": notification.type
            })
        
        # 计算未读数量
        unread_count = crud_sys_notification.filter(
            db, SysNotification.status == "unread"
        ).get_total()
        
        return success_response({
            "notifications": formatted_notifications,
            "total": total,
            "unread_count": unread_count,
            "page": page,
            "per_page": per_page
        })
    except Exception as e:
        logger.error(f"获取通知列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取通知列表失败: {str(e)}")


@router.post("/mark-all-read")
def mark_all_notifications_read(db: Session = Depends(get_db)):
    """
    标记所有通知为已读
    """
    try:
        # 获取所有未读通知
        unread_notifications = crud_sys_notification.filter(
            db, SysNotification.status == "unread"
        ).get_all()
        
        # 批量更新状态为已读
        for notification in unread_notifications:
            notification.status = "read"
        
        db.commit()
        
        return success_response({"message": "所有通知已标记为已读"})
    except Exception as e:
        logger.error(f"标记通知为已读失败: {e}")
        raise HTTPException(status_code=500, detail=f"标记通知为已读失败: {str(e)}")


@router.post("/clear")
def clear_all_notifications(db: Session = Depends(get_db)):
    """
    清空所有通知
    """
    try:
        # 获取所有通知
        all_notifications = crud_sys_notification.get_all(db)
        
        # 批量删除所有通知
        for notification in all_notifications:
            db.delete(notification)
        
        db.commit()
        
        return success_response({"message": "所有通知已清空"})
    except Exception as e:
        logger.error(f"清空通知失败: {e}")
        raise HTTPException(status_code=500, detail=f"清空通知失败: {str(e)}")


@router.post("/{notification_id}/read")
def mark_notification_read(notification_id: int, db: Session = Depends(get_db)):
    """
    标记单个通知为已读
    """
    try:
        # 获取指定通知
        notification = crud_sys_notification.get(db, notification_id)
        if not notification:
            raise HTTPException(status_code=404, detail=f"通知 {notification_id} 不存在")
        
        # 更新状态为已读
        notification.status = "read"
        db.commit()
        
        return success_response({"message": f"通知 {notification_id} 已标记为已读"})
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"标记通知为已读失败: {e}")
        raise HTTPException(status_code=500, detail=f"标记通知为已读失败: {str(e)}")
