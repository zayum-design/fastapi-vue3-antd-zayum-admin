import random
from typing import Generator, Dict, Any
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, exc
from sqlalchemy.sql import text
from datetime import datetime, timedelta, timezone

from app.main import app
from app.crud.sys_auth_admin import crud_sys_auth_admin
from app.schemas.sys_admin import SysAdminCreate
from app.dependencies.database import get_db
from app.core.security import create_access_token
from app.models.sys_admin import SysAdmin
from app.models.sys_admin_group import SysAdminGroup
from app.models.sys_admin_rule import SysAdminRule
from app.core.config import settings

# Constants
ADMIN_USER_ID = 1
BASE_API_URL = "/api/auth"

@pytest.fixture(scope="module")
def test_client() -> Generator[TestClient, None, None]:
    """创建测试客户端"""
    with TestClient(app) as client:
        yield client

@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """获取数据库会话"""
    db = next(get_db())
    try:
        db.execute(text("SELECT 1"))  # 测试数据库连接
        yield db
    except Exception as e:
        pytest.fail(f"数据库连接失败: {str(e)}")
    finally:
        db.rollback()
        db.close()

def create_test_admin(db: Session) -> SysAdmin:
    """创建测试管理员并返回"""
    admin_data = {
        "username": f"testadmin{random.randint(1000,9999)}",
        "password": "testpassword",
        "nickname": "测试管理员",
        "group_id": 1,
        "status": "normal"
    }
    admin = crud_sys_auth_admin.create(db, obj_in=SysAdminCreate(**admin_data))
    admin.set_password("testpassword")
    db.commit()
    return admin

def get_admin_token(db: Session, admin_id: int) -> str:
    """获取管理员token"""
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return create_access_token(
        data={"sub": admin_id}, expires_delta=access_token_expires
    )

def test_login(test_client: TestClient, db_session: Session):
    """测试管理员登录接口"""
    # 创建测试管理员
    admin = create_test_admin(db_session)
    
    # 准备登录数据
    login_data = {
        "username": admin.username,
        "password": "testpassword",
        "captcha": False
    }

    # 发送登录请求
    response = test_client.post(
        f"{BASE_API_URL}/login",
        json=login_data
    )

    # 验证响应
    assert response.status_code == 200
    data = response.json().get("data")
    assert "access_token" in data

def test_login_form(test_client: TestClient, db_session: Session):
    """测试表单登录接口"""
    # 创建测试管理员
    admin = create_test_admin(db_session)
    
    # 准备表单数据
    form_data = {
        "username": admin.username,
        "password": "testpassword",
        "grant_type": "password"
    }

    # 发送登录请求
    response = test_client.post(
        f"{BASE_API_URL}/login_form",
        data=form_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_get_profile(test_client: TestClient, db_session: Session):
    """测试获取管理员资料接口"""
    # 创建测试管理员
    admin = create_test_admin(db_session)
    token = get_admin_token(db_session, admin.id)
    
    # 创建测试管理员组
    group = SysAdminGroup(
        name="测试组",
        rules="1,2,3",
        status="normal"
    )
    db_session.add(group)
    db_session.commit()
    db_session.refresh(group)
    
    # 更新管理员组ID
    admin.group_id = group.id
    db_session.commit()

    # 请求管理员资料
    response = test_client.get(
        f"{BASE_API_URL}/profile",
        headers={"Authorization": f"Bearer {token}"}
    )

    # 验证响应
    assert response.status_code == 200
    data = response.json().get("data")
    assert data["username"] == admin.username
    assert data["roles"] == [group.name]

def test_update_profile(test_client: TestClient, db_session: Session):
    """测试更新管理员资料接口"""
    # 创建测试管理员
    admin = create_test_admin(db_session)
    token = get_admin_token(db_session, admin.id)
    
    # 准备更新数据
    update_data = {
        "nickname": "更新昵称",
        "email": "test@example.com",
        "mobile": "13800138000",
        "avatar": "/avatar/new.jpg"
    }

    # 发送更新请求
    response = test_client.post(
        f"{BASE_API_URL}/profile",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    # 验证响应
    assert response.status_code == 200
    
    # 验证数据库
    db_session.refresh(admin)
    assert admin.nickname == update_data["nickname"]
    assert admin.email == update_data["email"]

def test_get_access_codes(test_client: TestClient, db_session: Session):
    """测试获取访问权限码接口"""
    # 创建测试管理员和组
    group = SysAdminGroup(
        name="测试组",
        rules="1,2,3",
        status="normal",
        access=["code1", "code2"]
    )
    db_session.add(group)
    db_session.commit()
    
    admin = create_test_admin(db_session)
    admin.group_id = group.id
    db_session.commit()
    
    token = get_admin_token(db_session, admin.id)

    # 请求访问权限码
    response = test_client.get(
        f"{BASE_API_URL}/access_code",
        headers={"Authorization": f"Bearer {token}"}
    )

    # 验证响应
    assert response.status_code == 200
    data = response.json().get("data")
    assert data == ["code1", "code2"]

def test_refresh_token(test_client: TestClient, db_session: Session):
    """测试刷新token接口"""
    # 创建测试管理员
    admin = create_test_admin(db_session)
    token = get_admin_token(db_session, admin.id)

    # 请求刷新token
    response = test_client.post(
        f"{BASE_API_URL}/refresh_token",
        json={"refresh_token": token},
        headers={"Authorization": f"Bearer {token}"}
    )

    # 验证响应
    assert response.status_code == 200
    data = response.json().get("data")
    assert "access_token" in data
    assert data["access_token"] != token
