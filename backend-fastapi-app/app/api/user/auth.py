from typing import Annotated, Dict, List
from fastapi import APIRouter, HTTPException, status, Request, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_babel import _
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.models.sys_user_group import SysUserGroup
from app.models.sys_user_rule import SysUserRule
from app.schemas.sys_user import SysUser
from app.dependencies.database import get_db
from app.crud.sys_auth_user import crud_sys_auth_user
from app.core.security import (
    decode_access_token,
    get_current_user,
    verify_password,
    create_access_token,
)
from app.core.captcha import verify_captcha
from app.core.config import settings
from datetime import datetime, timedelta, timezone
from app.utils.log_utils import logger
from app.utils.responses import success_response
from app.crud.sys_user_rule import crud_sys_user_rule

router = APIRouter(prefix="/auth", tags=["user_auth"])


class LoginInput(BaseModel):
    username: str
    password: str
    captcha_type: str = "code"
    captcha: bool
    captcha_id: str | None = None
    captcha_code: str | None = None


class TokenData(BaseModel):
    access_token: str


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
    login_data: LoginInput,  # 接收登录数据
    request: Request,  # 接收请求对象，获取客户端 IP
    db: Session = Depends(get_db),
):
    # 验证验证码
    await verify_captcha(
        login_data.captcha_type,
        login_data.captcha,
        login_data.captcha_id,
        login_data.captcha_code,
    )

    client_ip = request.client.host  # 获取客户端 IP 地址

    # 查找管理员
    user = crud_sys_auth_user.get_by_name(db, username=login_data.username)

    if not user or not user.check_password(login_data.password):
        # user.set_password('111111')
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
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="用户名或密码错误"
        )

    # 登录成功，重置失败计数
    user.login_failure = 0
    user.login_time = datetime.now(timezone.utc)
    user.login_ip = client_ip

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
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
    # 验证验证码
    # await verify_captcha(form_data.captcha_id, form_data.captcha_code)  # 启用验证码验证

    client_ip = request.client.host  # 获取客户端 IP 地址
    logger.info(f"Login attempt from IP: {client_ip} with data: {form_data}")

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
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="用户名或密码错误"
        )

    # 登录成功，重置失败计数
    user.login_failure = 0
    user.login_time = datetime.now(timezone.utc)
    user.login_ip = client_ip

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    user.token = access_token
    db.commit()

    logger.info(
        f"User {form_data.username} logged in successfully from IP: {client_ip}"
    )

    return {"access_token": access_token, "token_type": "bearer"}


class ProfileInput(BaseModel):
    nickname: str | None = None
    email: str | None = None
    mobile: str | None = None
    avatar: str | None = None


@router.get("/profile")
async def get_profile(
    user: SysUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 获取角色名称
    group = db.query(SysUserGroup).filter(SysUserGroup.id == user.group_id).first()
    roles = group.name if group else None

    # 将角色名称添加到字典中
    user_dict = user.to_dict()
    user_dict["roles"] = [roles]

    return success_response(user_dict)


@router.post("/profile")
async def update_profile(
    profile_data: ProfileInput,
    user: SysUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    for field, value in profile_data.model_dump(exclude_unset=True).items():
        logger.warning(f"==========>: {user}, {field}, {value}")
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return success_response({})


@router.get("/access_code")
async def get_access_codes(
    user: SysUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    group = db.query(SysUserGroup).filter(SysUserGroup.id == user.group_id).first()
    access_codes = group.access
    return success_response(access_codes)


@router.get("/all_router")
async def get_all_router(
    user: SysUser = Depends(get_current_user), db: Session = Depends(get_db)
):
    group = db.query(SysUserGroup).filter(SysUserGroup.id == user.group_id).first()

    if group.rules == ["all"]:
        items = crud_sys_user_rule.get_all(db)
    else:
        items = crud_sys_user_rule.filter(SysUserGroup.rules == group.rules).get_all(
            db
        )
    return success_response(transform_items(items))


def transform_items(items: List[SysUserRule]) -> List[Dict]:
    # 定义一个递归函数，用于构建树形结构
    def build_tree(parent_id: int) -> List[Dict]:
        children = []
        for item in items:
            if item.parent_id == parent_id:
                # 构建子节点
                child = {
                    "id": item.id,
                    "name": item.name,
                    "path": f"/user{item.path}",
                    "component": item.component,  # component 使用 path 的值
                    "meta": item.meta,
                }
                # 递归构建子节点的 children
                child_children = build_tree(item.id)
                if child_children:
                    child["children"] = child_children
                children.append(child)
        return children

    # 找到所有顶级节点（parent_id=0）
    top_level_items = [item for item in items if item.parent_id == 0]

    # 为每个顶级节点构建独立的路由
    result = []
    for item in top_level_items:
        layout = {
            "id": item.id,
            "meta": item.meta,
            "name": item.name,
            "path": f"/user{item.path}",
            "redirect": (
                item.redirect if item.redirect else None
            ),  # 如果有 redirect 则使用，否则为 None
            "children": build_tree(item.id),  # 递归构建子节点
        }
        result.append(layout)

    return result


@router.post("/refresh_token", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str,  # 传入 refresh token
    db: Session = Depends(get_db),
):
    # 解码并验证 refresh_token
    payload = decode_access_token(refresh_token)

    # 如果解码失败或没有有效负载，抛出异常
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 获取用户ID并查询数据库
    user_id: int = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 查找用户或管理员
    user = db.query(SysUser).filter(SysUser.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    # 创建新的 access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )

    # 返回新的 access token
    return success_response({"access_token": access_token})
