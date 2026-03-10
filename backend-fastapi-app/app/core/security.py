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

from fastapi import Depends, HTTPException, Query, Request, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param


class OptionalOAuth2PasswordBearer(OAuth2PasswordBearer):
    """可选的 OAuth2 认证方案，没有 token 时不抛出异常"""
    
    async def __call__(self, request: Request) -> str | None:
        authorization = request.headers.get("Authorization")
        if not authorization:
            return None
        scheme, param = get_authorization_scheme_param(authorization)
        if scheme.lower() != "bearer":
            return None
        return param


from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.dependencies.database import get_db
from app.utils.log_utils import logger


# 使用可选的 OAuth2 方案（用于URL token支持）
optional_oauth2_admin_scheme = OptionalOAuth2PasswordBearer(tokenUrl="/api/admin/auth/login_form", auto_error=False)
optional_oauth2_user_scheme = OptionalOAuth2PasswordBearer(tokenUrl="/api/user/auth/login_form", auto_error=False)


# 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2PasswordBearer 实例，用于处理 OAuth2 认证
oauth2_admin_scheme = OAuth2PasswordBearer(tokenUrl="/api/admin/auth/login_form")
oauth2_user_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/auth/login_form")


async def get_token_from_request(
    request: Request,
    header_token: str | None = Depends(optional_oauth2_user_scheme),
    url_token: str | None = Query(None, alias="token", description="访问令牌(可通过URL参数传递)"),
) -> str | None:
    """从请求头或URL参数获取token
    
    优先级:
    1. 从OAuth2 scheme获取 (Authorization header)
    2. 从URL query参数获取 (?token=xxx)
    """
    # 如果OAuth2 scheme返回了有效token，使用它
    if header_token:
        return header_token
    
    # 否则尝试从URL参数获取，并去除Bearer前缀
    if url_token:
        return url_token.removeprefix("Bearer ")
    
    return None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证明文密码与哈希密码是否匹配"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None, token_type: str = "user") -> str:
    """
    创建访问令牌

    Args:
        data: 要编码到令牌中的数据
        expires_delta: 过期时间增量，默认为配置中的值
        token_type: 令牌类型，"user" 或 "admin"，用于区分用户和管理员

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
            "type": token_type,  # 添加令牌类型
        }
    )
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    logger.debug("JWT token generated", extra={"sub": data.get("sub"), "type": token_type, "exp": expire.isoformat()})
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
        logger.debug(f"Decoding token with SECRET_KEY={settings.SECRET_KEY[:10]}..., ALGORITHM={settings.ALGORITHM}")
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        logger.debug("JWT token decoded successfully", extra={"sub": payload.get("sub")})
        return payload
    except JWTError as e:
        logger.warning(f"JWT decode failed: {str(e)}, token={token[:50]}...")
        return None


async def get_admin_token_from_request(
    request: Request,
    header_token: str | None = Depends(optional_oauth2_admin_scheme),
    url_token: str | None = Query(None, alias="token", description="访问令牌(可通过URL参数传递)"),
) -> str | None:
    """从请求头或URL参数获取admin token
    
    优先级:
    1. 从OAuth2 scheme获取 (Authorization header)
    2. 从URL query参数获取 (?token=xxx)
    """
    if header_token:
        return header_token
    
    if url_token:
        return url_token.removeprefix("Bearer ")
    
    return None


async def get_current_admin(
    token: Annotated[str | None, Depends(get_admin_token_from_request)], db: Session = Depends(get_db)
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

    if not token:
        raise credentials_exception

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    # 验证令牌类型
    token_type: str = payload.get("type", "user")
    if token_type != "admin":
        logger.warning(f"Invalid token type for admin endpoint: {token_type}")
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


async def get_current_user(
    token: Annotated[str | None, Depends(get_token_from_request)], db: Session = Depends(get_db)
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

    if not token:
        raise credentials_exception

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    # 验证令牌类型
    token_type: str = payload.get("type", "user")
    if token_type != "user":
        logger.warning(f"Invalid token type for user endpoint: {token_type}")
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
