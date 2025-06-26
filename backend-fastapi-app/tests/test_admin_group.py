import random
from typing import Generator, Dict, Any
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, exc
from sqlalchemy.sql import text

from app.main import app
from app.crud.sys_admin_group import crud_sys_admin_group
from app.schemas.sys_admin_group import SysAdminGroupCreate, SysAdminGroupUpdate
from app.dependencies.database import get_db
from app.core.security import create_access_token
from app.models.sys_admin_group import SysAdminGroup

# Constants
ADMIN_USER_ID = 1
BASE_API_URL = "/api/admin/admin_group"

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

def generate_test_group_data() -> Dict[str, Any]:
    """生成测试管理员组数据"""
    rand = random.randint(1000, 9999)
    return {
        "name": f"测试组{rand}",
        "rules": "1,2,3",
        "status": "normal"
    }

def create_test_group(db: Session) -> SysAdminGroup:
    """创建测试管理员组并返回"""
    group_data = SysAdminGroupCreate(**generate_test_group_data())
    return crud_sys_admin_group.create(db, obj_in=group_data)

def test_read_group_list(test_client: TestClient, db_session: Session, admin_headers: Dict[str, str]):
    """测试获取管理员组列表接口"""
    # 创建测试组
    create_test_group(db_session)
    db_session.commit()

    # 请求组列表
    response = test_client.get(f"{BASE_API_URL}/list", headers=admin_headers)
    
    # 验证响应
    assert response.status_code == 200
    data = response.json().get("data")
    assert data["total"] > 0
    assert len(data["items"]) > 0

def test_read_single_group(test_client: TestClient, db_session: Session, admin_headers: Dict[str, str]):
    """测试获取单个管理员组接口"""
    # 创建测试组
    group = create_test_group(db_session)
    db_session.commit()

    # 请求组详情
    response = test_client.get(f"{BASE_API_URL}/{group.id}", headers=admin_headers)

    # 验证响应
    assert response.status_code == 200
    data = response.json().get("data")
    assert data["name"] == group.name
    assert data["rules"] == group.rules

def test_create_group(test_client: TestClient, db_session: Session, admin_headers: Dict[str, str]):
    """测试创建管理员组接口"""
    # 准备创建数据
    group_data = generate_test_group_data()
    
    # 发送创建请求
    response = test_client.post(
        f"{BASE_API_URL}/create", 
        json=group_data, 
        headers=admin_headers
    )

    # 验证响应
    assert response.status_code == 200
    data = response.json().get("data")
    assert "insert_id" in data

    # 验证数据库
    db_session.commit()
    group = crud_sys_admin_group.get(db_session, id=data["insert_id"])
    assert group is not None
    assert group.name == group_data["name"]

def test_update_group(test_client: TestClient, db_session: Session, admin_headers: Dict[str, str]):
    """测试更新管理员组接口"""
    # 创建测试组
    group = create_test_group(db_session)
    db_session.commit()
    db_session.refresh(group)

    # 准备更新数据
    update_data = {
        "id": group.id,
        "name": f"更新组{random.randint(1000,9999)}",
        "rules": "1,2,3,4",
        "status": "hidden"
    }
    
    # 创建更新模型
    update_model = SysAdminGroupUpdate(**update_data)

    # 发送更新请求
    response = test_client.put(
        f"{BASE_API_URL}/update/{group.id}",
        json=update_model.model_dump(exclude_unset=True),
        headers=admin_headers
    )

    # 验证响应
    assert response.status_code == 200
    data = response.json().get("data")
    assert data["name"] == update_data["name"]

    # 验证数据库
    db_session.commit()
    updated_group = crud_sys_admin_group.get(db_session, id=group.id)
    db_session.refresh(updated_group)
    assert updated_group is not None
    assert updated_group.name == update_data["name"]

def test_delete_group(test_client: TestClient, db_session: Session, admin_headers: Dict[str, str]):
    """测试删除管理员组接口"""
    # 创建测试组
    group = create_test_group(db_session)
    db_session.commit()
    db_session.refresh(group)
    
    # 发送删除请求
    response = test_client.delete(
        f"{BASE_API_URL}/delete/{group.id}", 
        headers=admin_headers
    )
    
    # 验证响应
    assert response.status_code == 200
    
    # 验证数据库
    db_session.commit()
    with pytest.raises(exc.ObjectDeletedError):
        crud_sys_admin_group.get(db_session, id=group.id)
