import random
from typing import Generator, Dict, Any
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, exc
from sqlalchemy.sql import text

from app.main import app
from app.crud.sys_plugin import crud_sys_plugin
from app.schemas.sys_plugin import SysPluginCreate, SysPluginUpdate
from app.dependencies.database import get_db
from app.core.security import create_access_token
from app.models.sys_plugin import SysPlugin

# Constants
ADMIN_USER_ID = 1
BASE_API_URL = "/api/admin/plugin"

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

def generate_test_plugin_data() -> Dict[str, Any]:
    """生成测试插件数据"""
    rand = random.randint(1000, 9999)
    return {
        "name": f"测试插件{rand}",
        "title": f"测试插件标题{rand}",
        "version": "1.0.0",
        "author": "测试作者",
        "description": "测试描述",
        "status": "normal"
    }

def create_test_plugin(db: Session) -> SysPlugin:
    """创建测试插件并返回"""
    plugin_data = SysPluginCreate(**generate_test_plugin_data())
    return crud_sys_plugin.create(db, obj_in=plugin_data)

def test_read_plugin_list(test_client: TestClient, db_session: Session, admin_headers: Dict[str, str]):
    """测试获取插件列表接口"""
    # 创建测试插件
    create_test_plugin(db_session)
    db_session.commit()

    # 请求插件列表
    response = test_client.get(f"{BASE_API_URL}/list", headers=admin_headers)
    
    # 验证响应
    assert response.status_code == 200
    data = response.json().get("data")
    assert data["total"] > 0
    assert len(data["items"]) > 0

def test_read_single_plugin(test_client: TestClient, db_session: Session, admin_headers: Dict[str, str]):
    """测试获取单个插件接口"""
    # 创建测试插件
    plugin = create_test_plugin(db_session)
    db_session.commit()

    # 请求插件详情
    response = test_client.get(f"{BASE_API_URL}/{plugin.id}", headers=admin_headers)

    # 验证响应
    assert response.status_code == 200
    data = response.json().get("data")
    assert data["name"] == plugin.name
    assert data["title"] == plugin.title

def test_create_plugin(test_client: TestClient, db_session: Session, admin_headers: Dict[str, str]):
    """测试创建插件接口"""
    # 准备创建数据
    plugin_data = generate_test_plugin_data()
    
    # 发送创建请求
    response = test_client.post(
        f"{BASE_API_URL}/create", 
        json=plugin_data, 
        headers=admin_headers
    )

    # 验证响应
    assert response.status_code == 200
    data = response.json().get("data")
    assert "insert_id" in data

    # 验证数据库
    db_session.commit()
    plugin = crud_sys_plugin.get(db_session, id=data["insert_id"])
    assert plugin is not None
    assert plugin.name == plugin_data["name"]

def test_update_plugin(test_client: TestClient, db_session: Session, admin_headers: Dict[str, str]):
    """测试更新插件接口"""
    # 创建测试插件
    plugin = create_test_plugin(db_session)
    db_session.commit()
    db_session.refresh(plugin)

    # 准备更新数据
    update_data = {
        "id": plugin.id,
        "name": f"更新插件{random.randint(1000,9999)}",
        "title": f"更新插件标题{random.randint(1000,9999)}",
        "version": "2.0.0",
        "author": "更新作者",
        "description": "更新描述",
        "status": "hidden"
    }
    
    # 创建更新模型
    update_model = SysPluginUpdate(**update_data)

    # 发送更新请求
    response = test_client.put(
        f"{BASE_API_URL}/update/{plugin.id}",
        json=update_model.model_dump(exclude_unset=True),
        headers=admin_headers
    )

    # 验证响应
    assert response.status_code == 200
    data = response.json().get("data")
    assert data["name"] == update_data["name"]

    # 验证数据库
    db_session.commit()
    updated_plugin = crud_sys_plugin.get(db_session, id=plugin.id)
    db_session.refresh(updated_plugin)
    assert updated_plugin is not None
    assert updated_plugin.name == update_data["name"]

def test_delete_plugin(test_client: TestClient, db_session: Session, admin_headers: Dict[str, str]):
    """测试删除插件接口"""
    # 创建测试插件
    plugin = create_test_plugin(db_session)
    db_session.commit()
    db_session.refresh(plugin)
    
    # 发送删除请求
    response = test_client.delete(
        f"{BASE_API_URL}/delete/{plugin.id}", 
        headers=admin_headers
    )
    
    # 验证响应
    assert response.status_code == 200
    
    # 验证数据库
    db_session.commit()
    with pytest.raises(exc.ObjectDeletedError):
        crud_sys_plugin.get(db_session, id=plugin.id)
