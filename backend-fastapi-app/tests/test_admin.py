import random
from typing import Generator, Dict, Any
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, exc
from sqlalchemy.sql import text

from app.main import app
from app.crud.sys_admin import crud_sys_admin
from app.schemas.sys_admin import SysAdminCreate, SysAdminUpdate
from app.dependencies.database import get_db
from app.core.security import create_access_token
from app.models.sys_admin import SysAdmin

# Constants
ADMIN_USER_ID = 1
TEST_PASSWORD = "AdminPass123"
BASE_API_URL = "/api/admin/admin"

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

def generate_test_admin_data() -> Dict[str, Any]:
    """生成测试管理员数据"""
    rand = random.randint(1000, 9999)
    return {
        "username": f"testadmin{rand}",
        "password": TEST_PASSWORD,
        "name": "测试管理员",
        "nickname": "测试管理员",
        "email": f"admin{rand}@example.com",
        "mobile": f"1380000{rand}",
        "group_id": 1,
        "status": "normal",
        "login_failure": 0
    }

def create_test_admin(db: Session) -> SysAdmin:
    """创建测试管理员并返回"""
    admin_data = SysAdminCreate(**generate_test_admin_data())
    return crud_sys_admin.create(db, obj_in=admin_data)

def test_read_admin_list(test_client: TestClient, db_session: Session, admin_headers: Dict[str, str]):
    """测试获取管理员列表接口"""
    # 创建测试管理员
    create_test_admin(db_session)
    db_session.commit()

    # 请求管理员列表
    response = test_client.get(f"{BASE_API_URL}/list", headers=admin_headers)
    
    # 验证响应
    assert response.status_code == 200
    data = response.json().get("data")
    assert data["total"] > 0
    assert len(data["items"]) > 0

def test_read_single_admin(test_client: TestClient, db_session: Session, admin_headers: Dict[str, str]):
    """测试获取单个管理员接口"""
    # 创建测试管理员
    admin = create_test_admin(db_session)
    db_session.commit()

    # 请求管理员详情
    response = test_client.get(f"{BASE_API_URL}/{admin.id}", headers=admin_headers)

    # 验证响应
    assert response.status_code == 200
    data = response.json().get("data")
    assert data["username"] == admin.username
    assert data["email"] == admin.email

def test_create_admin(test_client: TestClient, db_session: Session, admin_headers: Dict[str, str]):
    """测试创建管理员接口"""
    # 准备创建数据
    admin_data = generate_test_admin_data()
    new_admin = {
        "username": admin_data["username"],
        "password": TEST_PASSWORD,
        "nickname": admin_data["nickname"],
        "mobile": admin_data["mobile"],
        "email": admin_data["email"],
        "group_id": 1,
        "status": "normal",
        "login_failure": 0
    }

    # 发送创建请求
    response = test_client.post(
        f"{BASE_API_URL}/create", 
        json=new_admin, 
        headers=admin_headers
    )

    # 验证响应
    assert response.status_code == 200
    data = response.json().get("data")
    assert "insert_id" in data

    # 验证数据库
    db_session.commit()
    admin = crud_sys_admin.get(db_session, id=data["insert_id"])
    assert admin is not None
    assert admin.username == new_admin["username"]

def test_update_admin(test_client: TestClient, db_session: Session, admin_headers: Dict[str, str]):
    """测试更新管理员接口"""
    # 创建测试管理员
    admin = create_test_admin(db_session)
    db_session.commit()
    db_session.refresh(admin)

    # 准备更新数据
    update_data = {
        "id": admin.id,
        "username": admin.username,
        "nickname": admin.nickname,
        "password": admin.password,
        "email": f"updated{random.randint(1000,9999)}@example.com",
        "mobile": admin.mobile,
        "avatar": admin.avatar or "",
        "group_id": admin.group_id,
        "status": "normal"
    }
    
    # 创建更新模型
    update_model = SysAdminUpdate(**update_data)

    # 发送更新请求
    response = test_client.put(
        f"{BASE_API_URL}/update/{admin.id}",
        json=update_model.model_dump(exclude_unset=True),
        headers=admin_headers
    )

    # 验证响应
    assert response.status_code == 200
    data = response.json().get("data")
    assert data["email"] == update_data["email"]

    # 验证数据库
    db_session.commit()
    updated_admin = crud_sys_admin.get(db_session, id=admin.id)
    db_session.refresh(updated_admin)
    assert updated_admin is not None
    assert updated_admin.email == update_data["email"]

def test_delete_admin(test_client: TestClient, db_session: Session, admin_headers: Dict[str, str]):
    """测试删除管理员接口"""
    # 创建测试管理员
    admin = create_test_admin(db_session)
    db_session.commit()
    db_session.refresh(admin)
    
    # 发送删除请求
    response = test_client.delete(
        f"{BASE_API_URL}/delete/{admin.id}", 
        headers=admin_headers
    )
    
    # 验证响应
    assert response.status_code == 200
    
    # 验证数据库
    db_session.commit()
    with pytest.raises(exc.ObjectDeletedError):
        crud_sys_admin.get(db_session, id=admin.id)
