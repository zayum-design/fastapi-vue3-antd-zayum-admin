import random
from typing import Generator, Dict, Any
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, exc
from sqlalchemy.sql import text

from app.main import app
from app.crud.sys_general_config import crud_sys_general_config
from app.schemas.sys_general_config import SysGeneralConfigCreate, SysGeneralConfigUpdate
from app.dependencies.database import get_db
from app.core.security import create_access_token
from app.models.sys_general_config import SysGeneralConfig

# Constants
ADMIN_USER_ID = 1
BASE_API_URL = "/api/admin/general_config"

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

def generate_test_config_data() -> Dict[str, Any]:
    """生成测试通用配置数据"""
    rand = random.randint(1000, 9999)
    return {
        "name": f"测试配置{rand}",
        "code": f"test{rand}",
        "type": "string",
        "value": "test_value",
        "sort": 0,
        "status": "normal"
    }

def create_test_config(db: Session) -> SysGeneralConfig:
    """创建测试通用配置并返回"""
    config_data = SysGeneralConfigCreate(**generate_test_config_data())
    return crud_sys_general_config.create(db, obj_in=config_data)

def test_read_config_list(test_client: TestClient, db_session: Session, admin_headers: Dict[str, str]):
    """测试获取通用配置列表接口"""
    # 创建测试配置
    create_test_config(db_session)
    db_session.commit()

    # 请求配置列表
    response = test_client.get(f"{BASE_API_URL}/list", headers=admin_headers)
    
    # 验证响应
    assert response.status_code == 200
    data = response.json().get("data")
    assert data["total"] > 0
    assert len(data["items"]) > 0

def test_read_single_config(test_client: TestClient, db_session: Session, admin_headers: Dict[str, str]):
    """测试获取单个通用配置接口"""
    # 创建测试配置
    config = create_test_config(db_session)
    db_session.commit()

    # 请求配置详情
    response = test_client.get(f"{BASE_API_URL}/{config.id}", headers=admin_headers)

    # 验证响应
    assert response.status_code == 200
    data = response.json().get("data")
    assert data["name"] == config.name
    assert data["code"] == config.code

def test_create_config(test_client: TestClient, db_session: Session, admin_headers: Dict[str, str]):
    """测试创建通用配置接口"""
    # 准备创建数据
    config_data = generate_test_config_data()
    
    # 发送创建请求
    response = test_client.post(
        f"{BASE_API_URL}/create", 
        json=config_data, 
        headers=admin_headers
    )

    # 验证响应
    assert response.status_code == 200
    data = response.json().get("data")
    assert "insert_id" in data

    # 验证数据库
    db_session.commit()
    config = crud_sys_general_config.get(db_session, id=data["insert_id"])
    assert config is not None
    assert config.name == config_data["name"]

def test_update_config(test_client: TestClient, db_session: Session, admin_headers: Dict[str, str]):
    """测试更新通用配置接口"""
    # 创建测试配置
    config = create_test_config(db_session)
    db_session.commit()
    db_session.refresh(config)

    # 准备更新数据
    update_data = {
        "id": config.id,
        "name": f"更新配置{random.randint(1000,9999)}",
        "code": f"updated{random.randint(1000,9999)}",
        "type": "number",
        "value": "123",
        "sort": 1,
        "status": "hidden"
    }
    
    # 创建更新模型
    update_model = SysGeneralConfigUpdate(**update_data)

    # 发送更新请求
    response = test_client.put(
        f"{BASE_API_URL}/update/{config.id}",
        json=update_model.model_dump(exclude_unset=True),
        headers=admin_headers
    )

    # 验证响应
    assert response.status_code == 200
    data = response.json().get("data")
    assert data["name"] == update_data["name"]

    # 验证数据库
    db_session.commit()
    updated_config = crud_sys_general_config.get(db_session, id=config.id)
    db_session.refresh(updated_config)
    assert updated_config is not None
    assert updated_config.name == update_data["name"]

def test_delete_config(test_client: TestClient, db_session: Session, admin_headers: Dict[str, str]):
    """测试删除通用配置接口"""
    # 创建测试配置
    config = create_test_config(db_session)
    db_session.commit()
    db_session.refresh(config)
    
    # 发送删除请求
    response = test_client.delete(
        f"{BASE_API_URL}/delete/{config.id}", 
        headers=admin_headers
    )
    
    # 验证响应
    assert response.status_code == 200
    
    # 验证数据库
    db_session.commit()
    with pytest.raises(exc.ObjectDeletedError):
        crud_sys_general_config.get(db_session, id=config.id)
