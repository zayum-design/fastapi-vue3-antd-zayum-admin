import random
from typing import Generator, Dict, Any
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

from app.main import app
from app.crud.sys_general_config import crud_sys_general_config
from app.schemas.sys_general_config import SysGeneralConfigCreate
from app.dependencies.database import get_db
from app.core.security import create_access_token
from app.models.sys_general_config import SysGeneralConfig

# Constants
ADMIN_USER_ID = 1
BASE_API_URL = "/api/admin/config"

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
    """生成测试配置数据"""
    rand = random.randint(1000, 9999)
    return {
        "name": f"test_config_{rand}",
        "title": f"测试配置{rand}",
        "value": f"value_{rand}",
        "group": "system",
        "type": "string",
        "status": "normal"
    }

def create_test_config(db: Session) -> SysGeneralConfig:
    """创建测试配置并返回"""
    config_data = SysGeneralConfigCreate(**generate_test_config_data())
    return crud_sys_general_config.create(db, obj_in=config_data)

def test_read_config_list(test_client: TestClient, db_session: Session, admin_headers: Dict[str, str]):
    """测试获取配置列表接口"""
    # 创建测试配置
    config1 = create_test_config(db_session)
    config2 = create_test_config(db_session)
    db_session.commit()

    # 请求配置列表
    response = test_client.get(
        BASE_API_URL,
        headers=admin_headers
    )

    # 验证响应
    assert response.status_code == 200
    data = response.json().get("data")
    assert data["total"] >= 2
    assert len(data["items"]) >= 2
    assert any(item["name"] == config1.name for item in data["items"])
    assert any(item["name"] == config2.name for item in data["items"])
