import random
from typing import Generator, Dict, Any
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, exc
from sqlalchemy.sql import text

from app.main import app
from app.crud.sys_admin_log import crud_sys_admin_log
from app.schemas.sys_admin_log import SysAdminLogCreate, SysAdminLogUpdate
from app.dependencies.database import get_db
from app.core.security import create_access_token
from app.models.sys_admin_log import SysAdminLog

# Constants
ADMIN_USER_ID = 1
BASE_API_URL = "/api/admin/log"

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

def generate_test_admin_log_data() -> Dict[str, Any]:
    """生成测试管理员日志数据"""
    rand = random.randint(1000, 9999)
    return {
        "admin_id": 1,
        "username": f"admin{rand}",
        "url": f"/api/test/{rand}",
        "title": f"测试日志{rand}",
        "data": f"测试数据{rand}",
        "ip": f"127.0.0.{rand % 255}",
        "useragent": f"test-agent-{rand}",
        "status": "normal"
    }

def create_test_admin_log(db: Session) -> SysAdminLog:
    """创建测试管理员日志并返回"""
    log_data = SysAdminLogCreate(**generate_test_admin_log_data())
    return crud_sys_admin_log.create(db, obj_in=log_data)

def test_read_admin_log_list(test_client: TestClient, db_session: Session, admin_headers: Dict[str, str]):
    """测试获取管理员日志列表接口"""
    # 创建测试管理员日志
    create_test_admin_log(db_session)
    db_session.commit()

    # 请求管理员日志列表
    response = test_client.get(f"{BASE_API_URL}/list", headers=admin_headers)
    
    # 验证响应
    assert response.status_code == 200
    data = response.json().get("data")
    assert data["total"] > 0
    assert len(data["items"]) > 0

def test_read_single_admin_log(test_client: TestClient, db_session: Session, admin_headers: Dict[str, str]):
    """测试获取单个管理员日志接口"""
    # 创建测试管理员日志
    log = create_test_admin_log(db_session)
    db_session.commit()

    # 请求管理员日志详情
    response = test_client.get(f"{BASE_API_URL}/{log.id}", headers=admin_headers)

    # 验证响应
    assert response.status_code == 200
    data = response.json().get("data")
    assert data["title"] == log.title
    assert data["url"] == log.url

def test_create_admin_log(test_client: TestClient, db_session: Session, admin_headers: Dict[str, str]):
    """测试创建管理员日志接口"""
    # 准备创建数据
    log_data = generate_test_admin_log_data()
    new_log = {
        "admin_id": log_data["admin_id"],
        "username": log_data["username"],
        "url": log_data["url"],
        "title": log_data["title"],
        "data": log_data["data"],
        "ip": log_data["ip"],
        "useragent": log_data["useragent"],
        "status": log_data["status"]
    }

    # 发送创建请求
    response = test_client.post(
        f"{BASE_API_URL}/create", 
        json=new_log, 
        headers=admin_headers
    )

    # 验证响应
    assert response.status_code == 200
    data = response.json().get("data")
    assert "insert_id" in data

    # 验证数据库
    db_session.commit()
    log = crud_sys_admin_log.get(db_session, id=data["insert_id"])
    assert log is not None
    assert log.title == new_log["title"]

def test_update_admin_log(test_client: TestClient, db_session: Session, admin_headers: Dict[str, str]):
    """测试更新管理员日志接口"""
    # 创建测试管理员日志
    log = create_test_admin_log(db_session)
    db_session.commit()
    db_session.refresh(log)

    # 准备更新数据
    update_data = {
        "id": log.id,
        "admin_id": log.admin_id,
        "username": log.username,
        "url": f"/api/updated/{random.randint(1000,9999)}",
        "title": f"更新日志{random.randint(1000,9999)}",
        "data": f"更新数据{random.randint(1000,9999)}",
        "ip": f"127.0.0.{random.randint(1,255)}",
        "useragent": f"updated-agent-{random.randint(1000,9999)}",
        "status": "normal"
    }
    
    # 创建更新模型
    update_model = SysAdminLogUpdate(**update_data)

    # 发送更新请求
    response = test_client.put(
        f"{BASE_API_URL}/update/{log.id}",
        json=update_model.model_dump(exclude_unset=True),
        headers=admin_headers
    )

    # 验证响应
    assert response.status_code == 200
    data = response.json().get("data")
    assert data["title"] == update_data["title"]

    # 验证数据库
    db_session.commit()
    updated_log = crud_sys_admin_log.get(db_session, id=log.id)
    db_session.refresh(updated_log)
    assert updated_log is not None
    assert updated_log.title == update_data["title"]

def test_delete_admin_log(test_client: TestClient, db_session: Session, admin_headers: Dict[str, str]):
    """测试删除管理员日志接口"""
    # 创建测试管理员日志
    log = create_test_admin_log(db_session)
    db_session.commit()
    db_session.refresh(log)
    
    # 发送删除请求
    response = test_client.delete(
        f"{BASE_API_URL}/delete/{log.id}", 
        headers=admin_headers
    )
    
    # 验证响应
    assert response.status_code == 200
    
    # 验证数据库
    db_session.commit()
    with pytest.raises(exc.ObjectDeletedError):
        crud_sys_admin_log.get(db_session, id=log.id)
