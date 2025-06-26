from typing import Annotated
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from app.core.config import settings
from app.models.sys_admin import SysAdmin
from app.models.sys_user import SysUser
from app.dependencies.database import get_db
from sqlalchemy.orm import Session
from app.utils.log_utils import logger

# 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2PasswordBearer 实例，用于处理 OAuth2 认证
oauth2_admin_scheme = OAuth2PasswordBearer(tokenUrl="/api/admin/auth/login_form")
oauth2_user_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/auth/login_form")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update(
        {"exp": expire, "sub": str(data.get("sub"))}
    )  # 确保sub是字符串类型
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    logger.info(f"Generated token: {encoded_jwt}")  # 添加日志，便于调试
    return encoded_jwt


def decode_access_token(token: str):
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        logger.info(f"Decoded payload: {payload}")  # 日志记录解码结果
        return payload
    except JWTError as e:
        logger.error(f"JWTError: {str(e)}")
        return None


# 获取当前登录的 SysAdmin
def get_current_admin(
    token: Annotated[str, Depends(oauth2_admin_scheme)], db: Session = Depends(get_db)
) -> SysAdmin:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    admin_id: int = payload.get("sub")
    if admin_id is None:
        raise credentials_exception
    admin = db.query(SysAdmin).filter(SysAdmin.id == admin_id).first()
    if admin is None:
        logger.error("未能登录成功")
        raise credentials_exception
    logger.error(f"登录成功:{admin}")
    return admin


# 获取当前登录的 SysUser
def get_current_user(
    token: Annotated[str, Depends(oauth2_admin_scheme)], db: Session = Depends(get_db)
) -> SysAdmin:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    user_id: int = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    user = db.query(SysUser).filter(SysUser.id == user_id).first()
    if user is None:
        logger.error("未能登录成功")
        raise credentials_exception
    logger.error(f"登录成功:{user}")
    return user
