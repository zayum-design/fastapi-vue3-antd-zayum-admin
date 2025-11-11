# Standard library imports
from datetime import datetime, timedelta, timezone
from typing import Annotated, Dict, List, Literal

# Third-party imports
from fastapi import APIRouter, HTTPException, status, Request, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi_babel import _
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Local application imports
from app.core.captcha import verify_captcha
from app.core.config import settings
from app.core.security import (
    decode_access_token,
    get_current_user,
    verify_password,
    create_access_token,
)
from app.crud.sys_auth_user import crud_sys_auth_user
from app.crud.sys_user_rule import crud_sys_user_rule
from app.dependencies.database import get_db
from app.models.sys_user_group import SysUserGroup
from app.models.sys_user_rule import SysUserRule
from app.schemas.sys_user import SysUser, SysUserCreate
from app.utils.log_utils import logger
from app.utils.responses import success_response

router = APIRouter(prefix="/auth", tags=["user_auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login_form")


class LoginInput(BaseModel):
    username: str
    password: str
    captcha: bool


class SmsLoginInput(BaseModel):
    phone: str
    code: str


class QrLoginInput(BaseModel):
    qr_code: str


class RegisterInput(BaseModel):
    username: str
    password: str
    phone: str | None = None
    email: str | None = None
    platform: Literal['ios', 'mac', 'android', 'web', 'pc', 'other'] = "web"


class ForgotPasswordInput(BaseModel):
    username: str
    new_password: str
    code: str


class SocialLoginInput(BaseModel):
    type: str  # wechat/qq/weibo
    code: str  # 授权码


class TokenData(BaseModel):
    access_token: str
    user_info: dict | None = None


class TokenResponse(BaseModel):
    code: int
    msg: str
    data: TokenData
    time: str


class TokenForm(BaseModel):
    access_token: str
    token_type: str


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginInput,
    request: Request,
    db: Session = Depends(get_db),
):
    """用户账号密码登录接口

    Args:
        login_data: 包含用户名、密码的登录数据
        request: FastAPI请求对象
        db: 数据库会话

    Returns:
        TokenResponse: 包含access_token的响应

    Raises:
        HTTPException: 用户名或密码错误时抛出401异常
    """
    client_ip = str(getattr(request.client, "host",
                    "127.0.0.1"))  # type: ignore
    user = crud_sys_auth_user.get_by_name(db, username=login_data.username)

    if not user or not user.check_password(login_data.password):
        if user:
            user.login_failure += 1
            user.login_time = datetime.now(timezone.utc)
            user.login_ip = client_ip
            db.commit()
            logger.warning(
                f"Failed login attempt for user: {login_data.username} from IP: {client_ip}. Failure count: {user.login_failure}"
            )
        else:
            logger.warning(
                f"Failed login attempt for non-existent user: {login_data.username} from IP: {client_ip}"
            )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 登录成功处理
    user.login_failure = 0
    user.login_time = datetime.now(timezone.utc)
    user.login_ip = client_ip

    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    user.token = access_token
    db.commit()

    logger.info(
        f"User {login_data.username} logged in successfully from IP: {client_ip}"
    )

    return success_response({"access_token": access_token})


@router.post("/login_form", response_model=TokenForm)
async def login_form(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    """OAuth2标准表单登录接口

    Args:
        request: FastAPI请求对象
        form_data: OAuth2标准表单数据
        db: 数据库会话

    Returns:
        TokenForm: 包含access_token和token_type的响应

    Raises:
        HTTPException: 用户名或密码错误时抛出401异常
    """
    client_ip = request.client.host
    logger.info(
        f"Login attempt from IP: {client_ip} with username: {form_data.username}")

    user = crud_sys_auth_user.get_by_name(db, username=form_data.username)

    if not user or not user.check_password(form_data.password):
        if user:
            user.login_failure += 1
            user.login_time = datetime.now(timezone.utc)
            user.login_ip = client_ip
            db.commit()
            logger.warning(
                f"Failed login attempt for user: {form_data.username} from IP: {client_ip}. Failure count: {user.login_failure}"
            )
        else:
            logger.warning(
                f"Failed login attempt for non-existent user: {form_data.username} from IP: {client_ip}"
            )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 登录成功处理
    user.login_failure = 0
    user.login_time = datetime.now(timezone.utc)
    user.login_ip = client_ip

    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    user.token = access_token
    db.commit()

    logger.info(
        f"User {form_data.username} logged in successfully from IP: {client_ip}"
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/sms_login", response_model=TokenResponse)
async def sms_login(
    login_data: SmsLoginInput,
    request: Request,
    db: Session = Depends(get_db)
):
    # 模拟验证码验证
    if login_data.code != "123456":  # 测试用固定验证码
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码错误"
        )

    # 模拟查找用户
    # 模拟查找用户(这里固定返回测试用户)
    user = crud_sys_auth_user.get_by_name(db, username="test")
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )

    return success_response({
        "access_token": access_token,
        "user_info": {
            "username": "test_user",
            "phone": "13800000000"
        }
    })


@router.get("/sms_code")
async def get_sms_code(phone: str):
    # 模拟发送短信验证码
    return success_response({
        "message": f"验证码已发送到手机{phone}",
        "code": "123456"  # 测试用固定验证码
    })


@router.post("/qr_login", response_model=TokenResponse)
async def qr_login(
    login_data: QrLoginInput,
    request: Request,
    db: Session = Depends(get_db)
):
    # 模拟二维码验证
    if login_data.qr_code != "test_qr_code":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="二维码无效或已过期"
        )

    # 模拟查找用户(这里固定返回测试用户)
    # 模拟查找用户(这里固定返回测试用户)
    user = crud_sys_auth_user.get_by_name(db, username="test")
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )

    return success_response({
        "access_token": access_token,
        "user_info": {
            "username": "test_user",
            "phone": "13800000000"
        }
    })


@router.get("/qr_code")
async def get_qr_code():
    # 模拟生成二维码
    return success_response({
        "qr_code": "test_qr_code",
        "expire_time": 0
    })


@router.post("/register", response_model=TokenResponse)
async def register(
    register_data: RegisterInput,
    db: Session = Depends(get_db)
):
    # 检查用户名是否已存在
    if crud_sys_auth_user.get_by_name(db, username=register_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )

    # 创建用户
    user_data = SysUserCreate(
        id=None,
        user_group_id=1,
        username=register_data.username,
        password=register_data.password,
        mobile=register_data.phone if register_data.phone else "13800000000",
        email=register_data.email if register_data.email else f"{register_data.username}@example.com",
        nickname=register_data.username,
        status="normal",
        level=1,
        gender="male",
        score=0,
        platform=register_data.platform,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    user = crud_sys_auth_user.create(db, user_data)

    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )

    return success_response({
        "access_token": access_token,
        "user_info": {
            "username": "test_user",
            "phone": "13800000000"
        }
    })


@router.post("/forgot_password")
async def forgot_password(
    forgot_data: ForgotPasswordInput,
    db: Session = Depends(get_db)
):
    # 模拟验证码验证
    if forgot_data.code != "123456":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码错误"
        )

    # 更新密码
    user = crud_sys_auth_user.get_by_name(db, username=forgot_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    user.set_password(forgot_data.new_password)
    db.commit()

    return success_response({"message": "密码重置成功"})


@router.post("/social_login", response_model=TokenResponse)
async def social_login(
    login_data: SocialLoginInput,
    request: Request,
    db: Session = Depends(get_db)
):
    # 模拟第三方登录验证
    if login_data.code != "social_code":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="授权失败"
        )

    # 模拟查找或创建用户
    user = crud_sys_auth_user.get_by_name(
        db, username=f"{login_data.type}_user")
    if not user:
        user_data = SysUserCreate(
            id=None,
            user_group_id=1,
            username=f"{login_data.type}_user",
            password="social_password",
            mobile="13800000000",  # 默认手机号
            nickname=f"{login_data.type}_user",
            email=f"{login_data.type}_user@example.com",
            status="normal",
            level=1,
            gender="male",
            score=0,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        user = crud_sys_auth_user.create(db, user_data)

    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )

    return success_response({
        "access_token": access_token,
        "user_info": {
            "username": "test_user",
            "phone": "13800000000"
        }
    })


class ProfileInput(BaseModel):
    nickname: str | None = None
    email: str | None = None
    mobile: str | None = None
    avatar: str | None = None


@router.get("/profile")
async def get_profile(
    request: Request,
    current_user: SysUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户信息接口"""
    return success_response({
        "username": current_user.username,
        "nickname": current_user.nickname,
        "email": current_user.email,
        "phone": current_user.mobile,
        "avatar": current_user.avatar
    })


@router.post("/profile")
async def update_profile(
    profile_data: ProfileInput,
    current_user: SysUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    for field, value in profile_data.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return success_response({})


@router.get("/all_router")
async def get_all_router(
    current_user: SysUser = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    group = db.query(SysUserGroup).filter(
        SysUserGroup.id == current_user.user_group_id).first()
    items = crud_sys_user_rule.get_all(db)
    return success_response(transform_items(items))



def transform_items(items: List[SysUserRule]) -> List[Dict]:
    def build_tree(parent_id: int) -> List[Dict]:
        children = []
        for item in items:
            if item.parent_id == parent_id:
                child = {
                    "id": item.id,
                    "name": item.name,
                    "path": f"/admin{item.path}",
                    "component": item.component,
                    "meta": item.meta,
                }
                child_children = build_tree(item.id)
                if child_children:
                    child["children"] = child_children
                children.append(child)
        return children

    result = []
    for item in (item for item in items if item.parent_id == 0):
        layout = {
            "id": item.id,
            "meta": item.meta,
            "name": item.name,
            "path": f"/admin{item.path}",
            "redirect": item.redirect if item.redirect else None,
            "children": build_tree(item.id),
        }
        result.append(layout)
    return result


@router.post("/logout")
async def logout(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """用户登出接口

    Args:
        request: FastAPI请求对象
        token: 从请求头获取的JWT令牌
        db: 数据库会话

    Returns:
        成功或失败响应

    Raises:
        HTTPException: 当令牌无效或登出失败时抛出异常
    """
    try:
        # 验证令牌有效性
        payload = decode_access_token(token)
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的访问令牌"
            )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的用户ID"
            )

        # 获取用户并清除令牌
        user = crud_sys_auth_user.get(db, id=user_id)
        if user and user.token:
            user.token = None
            db.commit()
            logger.info(f"User {user.username} logged out successfully")
            return success_response({"message": "登出成功"})

        return success_response({"message": "用户未登录或已登出"})

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登出失败"
        )
