from typing import Annotated, Dict, List
from fastapi import APIRouter, HTTPException, status, Request, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_babel import _
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from app.models.sys_admin_group import SysAdminGroup
from app.models.sys_admin_rule import SysAdminRule
from app.models.sys_admin_log import SysAdminLog
from app.schemas.sys_admin import SysAdmin
from app.dependencies.database import get_db
from app.crud.sys_auth_admin import crud_sys_auth_admin
from app.crud.sys_admin_rule import crud_sys_admin_rule
from app.crud.sys_admin_log import crud_sys_admin_log
from app.core.security import (
    decode_access_token,
    get_current_admin,
    verify_password,
    create_access_token,
)
from app.core.captcha import verify_captcha
from app.core.config import settings
from app.utils.log_utils import logger
from app.utils.responses import success_response

router = APIRouter(prefix="/auth", tags=["auth"])


# Models
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


# Helper functions
def handle_failed_login(admin, username: str, client_ip: str, db: Session):
    if admin:
        admin.login_failure += 1
        admin.login_at = datetime.now(timezone.utc)
        admin.login_ip = client_ip
        db.commit()
        logger.warning(
            f"Failed login attempt for user: {username} from IP: {client_ip}. "
            f"Failure count: {admin.login_failure}"
        )
    else:
        logger.warning(
            f"Failed login attempt for non-existent user: {username} from IP: {client_ip}"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="用户名或密码错误"
    )


def handle_successful_login(admin, username: str, client_ip: str, db: Session):
    admin.login_failure = 0
    admin.login_at = datetime.now(timezone.utc)
    admin.login_ip = client_ip

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": admin.id}, expires_delta=access_token_expires
    )
    admin.token = access_token
    db.commit()

    logger.info(f"User {username} logged in successfully from IP: {client_ip}")
    return access_token


def transform_items(items: List[SysAdminRule]) -> List[Dict]:
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


# Routes
@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginInput,
    request: Request,
    db: Session = Depends(get_db),
):
    await verify_captcha(
        login_data.captcha_type,
        login_data.captcha,
        login_data.captcha_id,
        login_data.captcha_code,
    )

    admin = crud_sys_auth_admin.get_by_name(db, username=login_data.username)
    if not admin or not admin.check_password(login_data.password):
        handle_failed_login(admin, login_data.username, request.client.host, db)

    access_token = handle_successful_login(
        admin, login_data.username, request.client.host, db
    )
    return success_response({"access_token": access_token})


@router.post("/login_form", response_model=TokenForm)
async def login_form(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    admin = crud_sys_auth_admin.get_by_name(db, username=form_data.username)
    if not admin or not admin.check_password(form_data.password):
        handle_failed_login(admin, form_data.username, request.client.host, db)

    access_token = handle_successful_login(
        admin, form_data.username, request.client.host, db
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/profile")
async def get_profile(
    admin: SysAdmin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    group = db.query(SysAdminGroup).filter(SysAdminGroup.id == admin.group_id).first()
    admin_dict = admin.to_dict()
    admin_dict["roles"] = [group.name] if group else []
    
    log_items = crud_sys_admin_log.get_multi(
        db, 
        page=1, 
        per_page=6, 
        base_query=db.query(SysAdminLog).filter(SysAdminLog.admin_id == admin_dict["id"])
    )
    admin_dict["logs"] = [item.to_dict() for item in log_items]

    return success_response(admin_dict)


@router.post("/profile")
async def update_profile(
    profile_data: ProfileInput,
    admin: SysAdmin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    for field, value in profile_data.model_dump(exclude_unset=True).items():
        setattr(admin, field, value)
    db.commit()
    db.refresh(admin)
    return success_response({})


@router.get("/access_code")
async def get_access_codes(
    admin: SysAdmin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    group = db.query(SysAdminGroup).filter(SysAdminGroup.id == admin.group_id).first()
    return success_response(group.access if group else [])


@router.get("/all_router")
async def get_all_router(
    admin: SysAdmin = Depends(get_current_admin), db: Session = Depends(get_db)
):
    group = db.query(SysAdminGroup).filter(SysAdminGroup.id == admin.group_id).first()
    items = crud_sys_admin_rule.get_all(db)
    return success_response(transform_items(items))


@router.post("/refresh_token", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db),
):
    payload = decode_access_token(refresh_token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: int = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    admin = db.query(SysAdmin).filter(SysAdmin.id == user_id).first()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    access_token = create_access_token(
        data={"sub": admin.id},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return success_response({"access_token": access_token})
