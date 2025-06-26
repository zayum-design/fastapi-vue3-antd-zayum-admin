import random
from typing import Generator, Dict, Any
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, exc
from sqlalchemy.sql import text
from sqlalchemy import or_

from app.main import app
from app.crud.sys_user import crud_sys_user
from app.schemas.sys_user import SysUserCreate, SysUserUpdate
from app.dependencies.database import get_db
from app.core.security import create_access_token
from app.models.sys_user import SysUser

# Constants
ADMIN_USER_ID = 1
TEST_PASSWORD = "TestPass123"
BASE_API_URL = "/api/admin/user"

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

@pytest.fixture
def admin_headers() -> Dict[str, str]:
    """管理员认证头"""
    admin_token = create_access_token({"sub": ADMIN_USER_ID})
    return {"Authorization": f"Bearer {admin_token}"}

def generate_test_user_data() -> Dict[str, Any]:
    """生成测试用户数据"""
    rand = random.randint(1000, 9999)
    return {
        "username": f"testuser{rand}",
        "password": TEST_PASSWORD,
        "name": "测试用户",
        "nickname": "测试用户",
        "email": f"test{rand}@example.com",
        "mobile": f"1380000{rand}",
        "group_id": 1,
        "user_group_id": 1,
        "level": 0,
        "score": 0
    }

def create_test_user(db: Session) -> SysUser:
    """创建测试用户并返回"""
    user_data = SysUserCreate(**generate_test_user_data())
    return crud_sys_user.create(db, obj_in=user_data)

def test_read_user_list(test_client: TestClient, db_session: Session, admin_headers: Dict[str, str]):
    """测试获取用户列表接口"""
    # 创建测试用户
    create_test_user(db_session)
    db_session.commit()

    # 请求用户列表
    response = test_client.get(f"{BASE_API_URL}/list", headers=admin_headers)
    
    # 验证响应
    assert response.status_code == 200
    data = response.json().get("data")
    assert data["total"] > 0
    assert len(data["items"]) > 0

def test_read_single_user(test_client: TestClient, db_session: Session, admin_headers: Dict[str, str]):
    """测试获取单个用户接口"""
    # 创建测试用户
    user = create_test_user(db_session)
    db_session.commit()

    # 请求用户详情
    response = test_client.get(f"{BASE_API_URL}/{user.id}", headers=admin_headers)

    # 验证响应
    assert response.status_code == 200
    data = response.json().get("data")
    assert data["username"] == user.username
    assert data["email"] == user.email

def test_create_user(test_client: TestClient, db_session: Session, admin_headers: Dict[str, str]):
    """测试创建用户接口"""
    # 准备创建数据
    user_data = generate_test_user_data()
    new_user = {
        "username": user_data["username"],
        "password": TEST_PASSWORD,
        "nickname": user_data["nickname"],
        "mobile": user_data["mobile"],
        "email": user_data["email"],
        "user_group_id": 0,
        "level": 0,
        "score": 0
    }

    # 发送创建请求
    response = test_client.post(
        f"{BASE_API_URL}/create", 
        json=new_user, 
        headers=admin_headers
    )

    # 验证响应
    assert response.status_code == 200
    data = response.json().get("data")
    assert "insert_id" in data

    # 验证数据库
    db_session.commit()
    user = crud_sys_user.get(db_session, id=data["insert_id"])
    assert user is not None
    assert user.username == new_user["username"]

def test_update_user(test_client: TestClient, db_session: Session, admin_headers: Dict[str, str]):
    """测试更新用户接口"""
    # 创建测试用户
    user = create_test_user(db_session)
    db_session.commit()
    db_session.refresh(user)

    # 准备更新数据 - 确保所有必填字段都有值
    update_data = {
        "id": user.id,
        "user_group_id": user.user_group_id,
        "username": user.username,
        "nickname": user.nickname,
        "password": user.password,
        "email": f"updated{random.randint(1000,9999)}@example.com",
        "mobile": user.mobile,
        "avatar": user.avatar or "",
        "level": user.level,
        "gender": user.gender or 0,  # 确保gender有默认值
        "birthday": user.birthday or "2000-01-01",
        "bio": user.bio or "",
        "balance": float(user.balance or 0),
        "score": user.score,
        "successions": user.successions or 0,
        "max_successions": user.max_successions or 0,
        "prev_time": user.prev_time or "2000-01-01 00:00:00",
        "login_time": user.login_time or "2000-01-01 00:00:00",
        "login_ip": user.login_ip or "",
        "login_failure": user.login_failure or 0,
        "join_ip": user.join_ip or "",
        "verification": user.verification or "",
        "token": user.token or "",
        "status": "normal"
    }
    
    # 创建更新模型，确保所有字段都通过验证
    update_model = SysUserUpdate(**update_data)

    # 发送更新请求
    response = test_client.put(
        f"{BASE_API_URL}/update/{user.id}",
        json=update_model.model_dump(exclude_unset=True),
        headers=admin_headers
    )

    # 验证响应
    assert response.status_code == 200
    data = response.json().get("data")
    assert data["email"] == update_data["email"]

    # 验证数据库
    db_session.commit()
    updated_user = crud_sys_user.get(db_session, id=user.id)
    db_session.refresh(updated_user)
    assert updated_user is not None
    assert updated_user.email == update_data["email"]

def test_delete_user(test_client: TestClient, db_session: Session, admin_headers: Dict[str, str]):
    """测试删除用户接口"""
    # 创建测试用户
    user = create_test_user(db_session)
    db_session.commit()
    db_session.refresh(user)
    
    # 发送删除请求
    response = test_client.delete(
        f"{BASE_API_URL}/delete/{user.id}", 
        headers=admin_headers
    )
    
    # 验证响应
    assert response.status_code == 200
    
    # 验证数据库
    db_session.commit()
    with pytest.raises(exc.ObjectDeletedError):
        crud_sys_user.get(db_session, id=user.id)