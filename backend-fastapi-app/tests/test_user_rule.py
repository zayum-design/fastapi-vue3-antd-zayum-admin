import random
from typing import Generator, Dict, Any
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, exc
from sqlalchemy.sql import text

from app.main import app
from app.crud.sys_user_rule import crud_sys_user_rule
from app.schemas.sys_user_rule import SysUserRuleCreate, SysUserRuleUpdate
from app.dependencies.database import get_db
from app.core.security import create_access_token
from app.models.sys_user_rule import SysUserRule

# Constants
ADMIN_USER_ID = 1
BASE_API_URL = "/api/admin/user_rule"

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

def generate_test_user_rule_data() -> Dict[str, Any]:
    """生成测试用户规则数据"""
    rand = random.randint(1000, 9999)
    return {
        "name": f"测试用户规则{rand}",
        "title": f"测试规则标题{rand}",
        "type": "menu",
        "status": "normal",
        "condition": "",
        "sort": 0
    }

def create_test_user_rule(db: Session) -> SysUserRule:
    """创建测试用户规则并返回"""
    rule_data = SysUserRuleCreate(**generate_test_user_rule_data())
    return crud_sys_user_rule.create(db, obj_in=rule_data)

def test_read_user_rule_list(test_client: TestClient, db_session: Session, admin_headers: Dict[str, str]):
    """测试获取用户规则列表接口"""
    # 创建测试规则
    create_test_user_rule(db_session)
    db_session.commit()

    # 请求规则列表
    response = test_client.get(f"{BASE_API_URL}/list", headers=admin_headers)
    
    # 验证响应
    assert response.status_code == 200
    data = response.json().get("data")
    assert data["total"] > 0
    assert len(data["items"]) > 0

def test_read_single_user_rule(test_client: TestClient, db_session: Session, admin_headers: Dict[str, str]):
    """测试获取单个用户规则接口"""
    # 创建测试规则
    rule = create_test_user_rule(db_session)
    db_session.commit()

    # 请求规则详情
    response = test_client.get(f"{BASE_API_URL}/{rule.id}", headers=admin_headers)

    # 验证响应
    assert response.status_code == 200
    data = response.json().get("data")
    assert data["name"] == rule.name
    assert data["title"] == rule.title

def test_create_user_rule(test_client: TestClient, db_session: Session, admin_headers: Dict[str, str]):
    """测试创建用户规则接口"""
    # 准备创建数据
    rule_data = generate_test_user_rule_data()
    
    # 发送创建请求
    response = test_client.post(
        f"{BASE_API_URL}/create", 
        json=rule_data, 
        headers=admin_headers
    )

    # 验证响应
    assert response.status_code == 200
    data = response.json().get("data")
    assert "insert_id" in data

    # 验证数据库
    db_session.commit()
    rule = crud_sys_user_rule.get(db_session, id=data["insert_id"])
    assert rule is not None
    assert rule.name == rule_data["name"]

def test_update_user_rule(test_client: TestClient, db_session: Session, admin_headers: Dict[str, str]):
    """测试更新用户规则接口"""
    # 创建测试规则
    rule = create_test_user_rule(db_session)
    db_session.commit()
    db_session.refresh(rule)

    # 准备更新数据
    update_data = {
        "id": rule.id,
        "name": f"更新用户规则{random.randint(1000,9999)}",
        "title": f"更新规则标题{random.randint(1000,9999)}",
        "type": "button",
        "status": "hidden",
        "condition": "updated",
        "sort": 1
    }
    
    # 创建更新模型
    update_model = SysUserRuleUpdate(**update_data)

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
    updated_rule = crud_sys_user_rule.get(db_session, id=rule.id)
    db_session.refresh(updated_rule)
    assert updated_rule is not None
    assert updated_rule.name == update_data["name"]

def test_delete_user_rule(test_client: TestClient, db_session: Session, admin_headers: Dict[str, str]):
    """测试删除用户规则接口"""
    # 创建测试规则
    rule = create_test_user_rule(db_session)
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
        crud_sys_user_rule.get(db_session, id=rule.id)
