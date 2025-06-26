import random
from typing import Generator, Dict, Any
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, exc
from sqlalchemy.sql import text

from app.main import app
from app.crud.sys_admin_rule import crud_sys_admin_rule
from app.schemas.sys_admin_rule import SysAdminRuleCreate, SysAdminRuleUpdate
from app.dependencies.database import get_db
from app.core.security import create_access_token
from app.models.sys_admin_rule import SysAdminRule

# Constants
ADMIN_USER_ID = 1
BASE_API_URL = "/api/admin/rule"

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

def generate_test_admin_rule_data(parent_id: int = 0) -> Dict[str, Any]:
    """生成测试管理员规则数据"""
    rand = random.randint(1000, 9999)
    return {
        "parent_id": parent_id,
        "name": f"测试规则{rand}",
        "title": f"测试规则标题{rand}",
        "icon": f"icon-{rand}",
        "path": f"/test/{rand}",
        "component": f"TestComponent{rand}",
        "redirect": "",
        "status": "normal",
        "sort": rand % 100,
        "is_menu": 1,
        "is_show": 1,
        "is_auth": 1
    }

def create_test_admin_rule(db: Session, parent_id: int = 0) -> SysAdminRule:
    """创建测试管理员规则并返回"""
    rule_data = SysAdminRuleCreate(**generate_test_admin_rule_data(parent_id))
    return crud_sys_admin_rule.create(db, obj_in=rule_data)

def test_read_admin_rule_list(test_client: TestClient, db_session: Session, admin_headers: Dict[str, str]):
    """测试获取管理员规则列表接口(树形结构)"""
    # 创建测试规则
    parent_rule = create_test_admin_rule(db_session)
    child_rule = create_test_admin_rule(db_session, parent_id=parent_rule.id)
    db_session.commit()

    # 请求规则列表
    response = test_client.get(f"{BASE_API_URL}/list", headers=admin_headers)
    
    # 验证响应
    assert response.status_code == 200
    data = response.json().get("data")
    assert data["total"] > 0
    assert len(data["items"]) > 0
    
    # 验证树形结构
    parent_item = next((item for item in data["items"] if item["id"] == parent_rule.id), None)
    assert parent_item is not None
    assert any(child["id"] == child_rule.id for child in parent_item.get("children", []))

def test_read_single_admin_rule(test_client: TestClient, db_session: Session, admin_headers: Dict[str, str]):
    """测试获取单个管理员规则接口"""
    # 创建测试规则
    rule = create_test_admin_rule(db_session)
    db_session.commit()

    # 请求规则详情
    response = test_client.get(f"{BASE_API_URL}/{rule.id}", headers=admin_headers)

    # 验证响应
    assert response.status_code == 200
    data = response.json().get("data")
    assert data["name"] == rule.name
    assert data["title"] == rule.title

def test_create_admin_rule(test_client: TestClient, db_session: Session, admin_headers: Dict[str, str]):
    """测试创建管理员规则接口"""
    # 准备创建数据
    rule_data = generate_test_admin_rule_data()
    new_rule = {
        "parent_id": rule_data["parent_id"],
        "name": rule_data["name"],
        "title": rule_data["title"],
        "icon": rule_data["icon"],
        "path": rule_data["path"],
        "component": rule_data["component"],
        "status": rule_data["status"],
        "sort": rule_data["sort"],
        "is_menu": rule_data["is_menu"],
        "is_show": rule_data["is_show"],
        "is_auth": rule_data["is_auth"]
    }

    # 发送创建请求
    response = test_client.post(
        f"{BASE_API_URL}/create", 
        json=new_rule, 
        headers=admin_headers
    )

    # 验证响应
    assert response.status_code == 200
    data = response.json().get("data")
    assert "insert_id" in data

    # 验证数据库
    db_session.commit()
    rule = crud_sys_admin_rule.get(db_session, id=data["insert_id"])
    assert rule is not None
    assert rule.name == new_rule["name"]

def test_update_admin_rule(test_client: TestClient, db_session: Session, admin_headers: Dict[str, str]):
    """测试更新管理员规则接口"""
    # 创建测试规则
    rule = create_test_admin_rule(db_session)
    db_session.commit()
    db_session.refresh(rule)

    # 准备更新数据
    update_data = {
        "id": rule.id,
        "parent_id": rule.parent_id,
        "name": f"更新规则{random.randint(1000,9999)}",
        "title": f"更新规则标题{random.randint(1000,9999)}",
        "icon": f"updated-icon-{random.randint(1000,9999)}",
        "path": f"/updated/{random.randint(1000,9999)}",
        "component": f"UpdatedComponent{random.randint(1000,9999)}",
        "status": "normal",
        "sort": random.randint(1,100),
        "is_menu": 1,
        "is_show": 1,
        "is_auth": 1
    }
    
    # 创建更新模型
    update_model = SysAdminRuleUpdate(**update_data)

    # 发送更新请求
    response = test_client.put(
        f"{BASE_API_URL}/update/{rule.id}",
        json=update_model.model_dump(exclude_unset=True),
        headers=admin_headers
    )

    # 验证响应
    assert response.status_code == 200
    data = response.json().get("data")
    assert data["name"] == update_data["name"]

    # 验证数据库
    db_session.commit()
    updated_rule = crud_sys_admin_rule.get(db_session, id=rule.id)
    db_session.refresh(updated_rule)
    assert updated_rule is not None
    assert updated_rule.name == update_data["name"]

def test_delete_admin_rule(test_client: TestClient, db_session: Session, admin_headers: Dict[str, str]):
    """测试删除管理员规则接口"""
    # 创建测试规则
    rule = create_test_admin_rule(db_session)
    db_session.commit()
    db_session.refresh(rule)
    
    # 发送删除请求
    response = test_client.delete(
        f"{BASE_API_URL}/delete/{rule.id}", 
        headers=admin_headers
    )
    
    # 验证响应
    assert response.status_code == 200
    
    # 验证数据库
    db_session.commit()
    with pytest.raises(exc.ObjectDeletedError):
        crud_sys_admin_rule.get(db_session, id=rule.id)
