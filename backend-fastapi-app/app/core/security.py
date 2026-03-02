"""
安全认证模块
提供 JWT 认证、密码哈希等功能
"""

from typing import TYPE_CHECKING, Annotated

from passlib.context import CryptContext

if TYPE_CHECKING:
    from app.modules.admin.sys_admin.models.sys_admin import SysAdmin
    from app.modules.admin.sys_user.models.sys_user import SysUser
from datetime import UTC, datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.dependencies.database import get_db
from app.utils.log_utils import logger

# 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2PasswordBearer 实例，用于处理 OAuth2 认证
oauth2_admin_scheme = OAuth2PasswordBearer(tokenUrl="/api/admin/auth/login_form")
oauth2_user_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/auth/login_form")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证明文密码与哈希密码是否匹配"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    创建访问令牌

    Args:
        data: 要编码到令牌中的数据
        expires_delta: 过期时间增量，默认为配置中的值

    Returns:
        str: JWT 令牌
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update(
        {
            "exp": expire,
            "sub": str(data.get("sub")),  # 确保 sub 是字符串类型
        }
    )
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    logger.debug("JWT token generated", extra={"sub": data.get("sub"), "exp": expire.isoformat()})
    return encoded_jwt


def decode_access_token(token: str) -> dict | None:
    """
    解码访问令牌

    Args:
        token: JWT 令牌

    Returns:
        Optional[dict]: 解码后的 payload，失败返回 None
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        logger.debug("JWT token decoded successfully", extra={"sub": payload.get("sub")})
        return payload
    except JWTError:
        logger.warning("JWT decode failed: {str(e)}")
        return None


def get_current_admin(
    token: Annotated[str, Depends(oauth2_admin_scheme)], db: Session = Depends(get_db)
) -> "SysAdmin":
    """
    获取当前登录的管理员

    Args:
        token: JWT 令牌
        db: 数据库会话

    Returns:
        SysAdmin: 当前管理员对象

    Raises:
        HTTPException: 认证失败时抛出
    """
    from app.modules.admin.sys_admin.models.sys_admin import SysAdmin

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    admin_id: str = payload.get("sub")
    if admin_id is None:
        raise credentials_exception

    try:
        admin_id_int: int = int(admin_id)
    except (ValueError, TypeError):
        logger.warning("Invalid admin ID format in token: {admin_id}")
        raise credentials_exception

    admin = db.query(SysAdmin).filter(SysAdmin.id == admin_id_int).first()
    if admin is None:
        logger.warning("Admin not found for ID: {admin_id_int}")
        raise credentials_exception

    logger.info(
        "Admin authenticated: {admin.username}",
        extra={"admin_id": admin.id, "username": admin.username},
    )
    return admin


def get_current_user(
    token: Annotated[str, Depends(oauth2_user_scheme)], db: Session = Depends(get_db)
) -> "SysUser":
    """
    获取当前登录的用户

    Args:
        token: JWT 令牌
        db: 数据库会话

    Returns:
        SysUser: 当前用户对象

    Raises:
        HTTPException: 认证失败时抛出
    """
    from app.modules.admin.sys_user.models.sys_user import SysUser

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    try:
        user_id_int: int = int(user_id)
    except (ValueError, TypeError):
        logger.warning("Invalid user ID format in token: {user_id}")
        raise credentials_exception

    user = db.query(SysUser).filter(SysUser.id == user_id_int).first()
    if user is None:
        logger.warning("User not found for ID: {user_id_int}")
        raise credentials_exception

    logger.info(
        "User authenticated: {user.username}", extra={"user_id": user.id, "username": user.username}
    )
    return user
