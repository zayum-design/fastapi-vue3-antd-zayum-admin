"""
认证依赖模块
提供 FastAPI 认证相关的依赖注入
"""

from typing import TYPE_CHECKING, Annotated, Optional

from fastapi import Depends, HTTPException, status

if TYPE_CHECKING:
    from app.modules.admin.sys_admin.models.sys_admin import SysAdmin
    from app.modules.admin.sys_user.models.sys_user import SysUser
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.utils.log_utils import logger

# OAuth2 方案
oauth2_admin_scheme = OAuth2PasswordBearer(tokenUrl="/api/admin/auth/login_form", auto_error=False)

oauth2_user_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/auth/login_form", auto_error=False)


class AuthenticationError(HTTPException):
    """认证错误"""

    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_admin(
    token: Annotated[str | None, Depends(oauth2_admin_scheme)], db: Session = Depends(get_db)
) -> "SysAdmin":
    """
    获取当前登录的管理员

    Args:
        token: JWT 令牌
        db: 数据库会话

    Returns:
        SysAdmin: 当前管理员对象

    Raises:
        AuthenticationError: 认证失败时抛出
    """
    from app.modules.admin.sys_admin.models.sys_admin import SysAdmin

    if not token:
        raise AuthenticationError("Authentication required")

    from app.core.security import decode_access_token

    payload = decode_access_token(token)
    if payload is None:
        raise AuthenticationError("Invalid token")

    admin_id: str = payload.get("sub")
    if admin_id is None:
        raise AuthenticationError("Invalid token payload")

    try:
        admin_id_int: int = int(admin_id)
    except (ValueError, TypeError):
        logger.warning("Invalid admin ID format in token: {admin_id}")
        raise AuthenticationError("Invalid user ID format")

    admin = db.query(SysAdmin).filter(SysAdmin.id == admin_id_int).first()
    if admin is None:
        logger.warning("Admin not found for ID: {admin_id_int}")
        raise AuthenticationError("User not found")

    if admin.status != "normal":
        raise AuthenticationError("Account is disabled")

    logger.debug(
        "Admin authenticated: {admin.username}",
        extra={"admin_id": admin.id, "username": admin.username},
    )
    return admin


def get_optional_admin(
    token: Annotated[str | None, Depends(oauth2_admin_scheme)], db: Session = Depends(get_db)
) -> Optional["SysAdmin"]:
    """
    获取当前管理员（可选，不强制认证）

    Returns:
        SysAdmin or None: 如果已认证返回管理员对象，否则返回 None
    """
    if not token:
        return None

    try:
        return get_current_admin(token, db)
    except AuthenticationError:
        return None


def get_current_user(
    token: Annotated[str | None, Depends(oauth2_user_scheme)], db: Session = Depends(get_db)
) -> "SysUser":
    """
    获取当前登录的用户

    Args:
        token: JWT 令牌
        db: 数据库会话

    Returns:
        SysUser: 当前用户对象

    Raises:
        AuthenticationError: 认证失败时抛出
    """
    from app.modules.admin.sys_user.models.sys_user import SysUser

    if not token:
        raise AuthenticationError("Authentication required")

    from app.core.security import decode_access_token

    payload = decode_access_token(token)
    if payload is None:
        raise AuthenticationError("Invalid token")

    user_id: str = payload.get("sub")
    if user_id is None:
        raise AuthenticationError("Invalid token payload")

    try:
        user_id_int: int = int(user_id)
    except (ValueError, TypeError):
        logger.warning("Invalid user ID format in token: {user_id}")
        raise AuthenticationError("Invalid user ID format")

    user = db.query(SysUser).filter(SysUser.id == user_id_int).first()
    if user is None:
        logger.warning("User not found for ID: {user_id_int}")
        raise AuthenticationError("User not found")

    if user.status != "normal":
        raise AuthenticationError("Account is disabled")

    logger.debug(
        "User authenticated: {user.username}", extra={"user_id": user.id, "username": user.username}
    )
    return user


def require_permissions(permissions: list[str]):
    """
    权限检查依赖工厂

    Usage:
        @router.delete("/admin/{id}")
        async def delete_admin(
            admin_id: int,
            current_admin: SysAdmin = Depends(require_permissions(["admin:delete"]))
        ):
            ...
    """

    def check_permissions(admin: "SysAdmin" = Depends(get_current_admin)) -> "SysAdmin":
        # TODO: 实现实际的权限检查逻辑
        # 这里简化处理，实际应该从数据库或缓存中检查用户权限
        logger.debug("Checking permissions for {admin.username}: {permissions}")
        return admin

    return check_permissions


# 便捷依赖别名
CurrentAdmin = Annotated["SysAdmin", Depends(get_current_admin)]
CurrentUser = Annotated["SysUser", Depends(get_current_user)]
OptionalAdmin = Annotated[Optional["SysAdmin"], Depends(get_optional_admin)]
