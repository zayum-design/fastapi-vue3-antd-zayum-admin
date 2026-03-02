"""
认证 API 路由
提供登录、登出、Token 刷新等功能
"""

from collections import defaultdict
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.dependencies.auth import CurrentAdmin
from app.dependencies.database import get_db
from app.exceptions import UnauthorizedError
from app.modules.admin.sys_admin.services.sys_admin import sys_admin_service
from app.modules.admin.sys_admin_group.models.sys_admin_group import SysAdminGroup
from app.modules.admin.sys_admin_log.crud.sys_admin_log import crud_sys_admin_log
from app.modules.admin.sys_admin_log.models.sys_admin_log import SysAdminLog
from app.modules.admin.sys_admin_rule.crud.sys_admin_rule import crud_sys_admin_rule
from app.modules.admin.sys_admin_rule.models.sys_admin_rule import SysAdminRule
from app.utils.log_utils import logger
from app.utils.responses import success_response

router = APIRouter(prefix="/auth", tags=["auth"])


# ============== Pydantic Schemas ==============


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


class ProfileInput(BaseModel):
    nickname: str | None = None
    email: str | None = None
    mobile: str | None = None
    avatar: str | None = None


# ============== Helper Functions ==============


def get_client_ip(request: Request) -> str:
    """获取客户端 IP 地址"""
    return getattr(request.client, "host", "unknown") if request.client else "unknown"


def transform_items(items: list[SysAdminRule]) -> list[dict]:
    """
    将权限规则列表转换为树形结构

    优化后的算法使用字典提高查找性能
    """
    items_by_parent = defaultdict(list)
    root_items = []

    for item in items:
        if item.parent_id == 0:
            root_items.append(item)
        items_by_parent[item.parent_id].append(item)

    def build_tree(parent_id: int) -> list[dict]:
        return [
            {
                "id": item.id,
                "name": item.name,
                "path": f"{item.path}",
                "component": item.component,
                "meta": item.meta,
                **({"children": build_tree(item.id)} if items_by_parent[item.id] else {}),
            }
            for item in items_by_parent[parent_id]
        ]

    return [
        {
            "id": item.id,
            "meta": item.meta,
            "name": item.name,
            "path": f"/admin{item.path}",
            "redirect": item.redirect if item.redirect else None,
            "children": build_tree(item.id),
        }
        for item in root_items
    ]


# ============== Auth Endpoints ==============


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginInput,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    用户登录（JSON 格式）

    支持验证码验证
    """
    client_ip = get_client_ip(request)

    # 验证码验证
    # if login_data.captcha_type == "code":
    #     if not login_data.captcha_id or not login_data.captcha_code:
    #         raise HTTPException(
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #             detail="验证码参数缺失"
    #         )

    #     captcha_valid = await verify_captcha(
    #         login_data.captcha_type,
    #         login_data.captcha,
    #         login_data.captcha_id,
    #         login_data.captcha_code,
    #     )
    #     if not captcha_valid:
    #         raise HTTPException(
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #             detail=f"验证码错误或已过期{captcha_valid}-{ login_data.captcha_type}, {login_data.captcha}, {login_data.captcha_id},{login_data.captcha_code},"
    #         )

    # 使用 Service 层进行认证
    admin = sys_admin_service.authenticate(
        db, username=login_data.username, password=login_data.password
    )

    if not admin:
        logger.warning(f"Failed login attempt for {login_data.username} from IP: {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 刷新对象状态，防止 session 过期导致 "0 were matched" 错误
    db.refresh(admin)

    # 更新登录信息
    admin.login_ip = client_ip
    db.commit()

    # 生成 Token
    access_token = sys_admin_service.create_access_token_for_admin(admin)

    # 保存 Token 到数据库
    admin.token = access_token
    db.commit()

    logger.info("User {admin.username} logged in successfully from IP: {client_ip}")

    return success_response({"access_token": access_token})


@router.post("/login_form", response_model=TokenForm)
async def login_form(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    """
    用户登录（OAuth2 表单格式）

    用于 Swagger UI 等 OAuth2 客户端
    """
    client_ip = get_client_ip(request)

    # 使用 Service 层进行认证
    admin = sys_admin_service.authenticate(
        db, username=form_data.username, password=form_data.password
    )

    if not admin:
        logger.warning(f"Failed login attempt for {form_data.username} from IP: {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 刷新对象状态，防止 session 过期导致 "0 were matched" 错误
    db.refresh(admin)

    # 更新登录信息
    admin.login_ip = client_ip
    db.commit()

    # 生成 Token
    access_token = sys_admin_service.create_access_token_for_admin(admin)

    # 保存 Token 到数据库
    admin.token = access_token
    db.commit()

    logger.info("User {admin.username} logged in successfully from IP: {client_ip}")

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/profile")
async def get_profile(
    admin: CurrentAdmin = None,
    db: Session = Depends(get_db),
):
    """获取当前用户资料"""
    if not admin:
        raise UnauthorizedError("Authentication required")

    group = db.query(SysAdminGroup).filter(SysAdminGroup.id == admin.group_id).first()

    # 获取最近的操作日志
    base_query = db.query(SysAdminLog).filter(SysAdminLog.admin_id == admin.id)
    log_items = crud_sys_admin_log.get_multi(
        db, page=1, per_page=8, orderby="id_desc", base_query=base_query
    )

    admin_dict = admin.to_dict()
    admin_dict["roles"] = [group.name] if group else []
    admin_dict["logs"] = [item.to_dict() for item in log_items]

    return success_response(admin_dict)


@router.post("/profile")
async def update_profile(
    profile_data: ProfileInput,
    admin: CurrentAdmin = None,
    db: Session = Depends(get_db),
):
    """更新当前用户资料"""
    if not admin:
        raise UnauthorizedError("Authentication required")

    for field, value in profile_data.model_dump(exclude_unset=True).items():
        setattr(admin, field, value)

    db.commit()
    db.refresh(admin)

    logger.info("Profile updated for user: {admin.username}")
    return success_response({"message": "Profile updated successfully"})


@router.get("/access_code")
async def get_access_codes(
    admin: CurrentAdmin = None,
    db: Session = Depends(get_db),
):
    """获取当前用户的权限代码列表"""
    if not admin:
        raise UnauthorizedError("Authentication required")

    group = db.query(SysAdminGroup).filter(SysAdminGroup.id == admin.group_id).first()
    return success_response(group.access if group else [])


@router.get("/all_router")
async def get_all_router(admin: CurrentAdmin = None, db: Session = Depends(get_db)):
    """获取所有路由（菜单）结构"""
    if not admin:
        raise UnauthorizedError("Authentication required")

    items = crud_sys_admin_rule.get_all(db)
    return success_response(transform_items(items))


@router.post("/refresh_token", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db),
):
    """刷新访问令牌"""
    payload = decode_access_token(refresh_token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id_raw = payload.get("sub")
    if user_id_raw is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id: int = int(user_id_raw)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    admin = sys_admin_service.get(db, user_id)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    # 生成新的 Token
    access_token = sys_admin_service.create_access_token_for_admin(admin)

    # 更新数据库中的 Token
    admin.token = access_token
    db.commit()

    logger.info("Token refreshed for user: {admin.username}")
    return success_response({"access_token": access_token})


@router.post("/logout")
async def logout(
    admin: CurrentAdmin = None,
    db: Session = Depends(get_db),
):
    """用户登出"""
    if not admin:
        return success_response({"message": "Logout successful"})

    # 清除用户的 token
    admin.token = None
    db.commit()

    logger.info("User {admin.username} logged out successfully")
    return success_response({"message": "Logout successful"})
