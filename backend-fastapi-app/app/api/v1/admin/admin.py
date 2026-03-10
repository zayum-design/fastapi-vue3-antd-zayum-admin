"""
SysAdmin API 路由
提供管理员管理接口

架构分层：
- API Layer (Routes): 处理 HTTP 请求/响应
- Service Layer: 处理业务逻辑（SysAdminService）
- Repository Layer: 处理数据访问（SysAdminRepository）
"""

from fastapi import APIRouter, Depends, Query
from fastapi_babel import _
from sqlalchemy.orm import Session

from app.dependencies.auth import CurrentAdmin, get_current_admin
from app.dependencies.database import get_db
from app.exceptions import NotFoundError
from app.modules.admin.sys_admin.schemas.sys_admin import SysAdminCreate, SysAdminUpdate
from app.modules.admin.sys_admin.services.sys_admin import sys_admin_service
from app.utils.responses import success_response

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(get_current_admin)])


# ============== Admin Management Endpoints ==============


@router.get("/list")
def list_admins(
    page: int = Query(1, ge=1, description="页码"),
    per_page: int = Query(10, ge=1, le=200, description="每页数量"),
    search: str | None = Query(None, description="搜索关键词"),
    orderby: str | None = Query(None, description="排序，如 'created_at_desc'"),
    status: str | None = Query(None, description="状态过滤"),
    group_id: int | None = Query(None, description="分组ID过滤"),
    db: Session = Depends(get_db),
):
    """
    获取管理员列表

    支持分页、搜索、排序和状态过滤
    """
    items, total = sys_admin_service.get_admin_list(
        db,
        page=page,
        per_page=per_page,
        search=search,
        orderby=orderby,
        status=status,
        group_id=group_id,
    )

    return success_response(
        {
            "items": [item.to_dict() for item in items],
            "total": total,
            "page": page,
            "per_page": per_page,
        }
    )


@router.get("/{admin_id}")
def get_admin(admin_id: int, db: Session = Depends(get_db)):
    """获取单个管理员详情"""
    admin = sys_admin_service.get(db, admin_id)
    if not admin:
        raise NotFoundError(_("Admin not found"))
    return success_response(admin.to_dict())


@router.post("/create")
def create_admin(
    obj_in: SysAdminCreate, db: Session = Depends(get_db), current_admin: CurrentAdmin = None
):
    """创建管理员"""
    admin = sys_admin_service.create_admin(
        db, obj_in=obj_in, created_by=current_admin.id if current_admin else None
    )
    return success_response(
        {"id": admin.id, "username": admin.username, "message": _("Admin created successfully")}
    )


@router.put("/update/{admin_id}")
def update_admin(
    admin_id: int,
    obj_in: SysAdminUpdate,
    db: Session = Depends(get_db),
    current_admin: CurrentAdmin = None,
):
    """更新管理员"""
    admin = sys_admin_service.update_admin(
        db, admin_id=admin_id, obj_in=obj_in, updated_by=current_admin.id if current_admin else None
    )
    return success_response(admin.to_dict())


@router.delete("/delete/{admin_id}")
def delete_admin(admin_id: int, db: Session = Depends(get_db)):
    """删除管理员"""
    # 检查是否存在
    if not sys_admin_service.exists(db, admin_id):
        raise NotFoundError(_("Admin not found"))

    sys_admin_service.delete(db, admin_id)
    return success_response({"message": _("Admin deleted successfully")})


# ============== Admin Action Endpoints ==============


@router.post("/{admin_id}/toggle-status")
def toggle_admin_status(
    admin_id: int, db: Session = Depends(get_db), current_admin: CurrentAdmin = None
):
    """切换管理员状态（启用/禁用）"""
    admin = sys_admin_service.toggle_status(db, admin_id)
    return success_response(
        {"id": admin.id, "status": admin.status, "message": _("Status toggled successfully")}
    )


@router.post("/{admin_id}/unlock")
def unlock_admin(admin_id: int, db: Session = Depends(get_db), current_admin: CurrentAdmin = None):
    """解锁被锁定的管理员账户"""
    admin = sys_admin_service.unlock_account(db, admin_id)
    return success_response(
        {
            "id": admin.id,
            "login_failure": admin.login_failure,
            "message": _("Account unlocked successfully"),
        }
    )


@router.post("/{admin_id}/reset-password")
def reset_admin_password(
    admin_id: int,
    new_password: str,
    db: Session = Depends(get_db),
    current_admin: CurrentAdmin = None,
):
    """重置管理员密码"""
    admin = sys_admin_service.reset_password(
        db,
        admin_id=admin_id,
        new_password=new_password,
        reset_by=current_admin.id if current_admin else None,
    )
    return success_response({"id": admin.id, "message": _("Password reset successfully")})
