import random
from typing import Generator, Dict, Any
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, exc
from sqlalchemy.sql import text

from app.main import app
from app.crud.sys_attachment_category import crud_sys_attachment_category
from app.schemas.sys_attachment_category import SysAttachmentCategoryCreate, SysAttachmentCategoryUpdate
from app.dependencies.database import get_db
from app.core.security import create_access_token
from app.models.sys_attachment_category import SysAttachmentCategory

# Constants
ADMIN_USER_ID = 1
BASE_API_URL = "/api/admin/attachment_category"

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

def generate_test_category_data() -> Dict[str, Any]:
    """生成测试附件分类数据"""
    rand = random.randint(1000, 9999)
    return {
        "name": f"测试分类{rand}",
        "code": f"test{rand}",
        "max_size": 1024,
        "extensions": "jpg,png",
        "mime_types": "image/jpeg,image/png",
        "status": "normal"
    }

def create_test_category(db: Session) -> SysAttachmentCategory:
    """创建测试附件分类并返回"""
    category_data = SysAttachmentCategoryCreate(**generate_test_category_data())
    return crud_sys_attachment_category.create(db, obj_in=category_data)

def test_read_category_list(test_client: TestClient, db_session: Session, admin_headers: Dict[str, str]):
    """测试获取附件分类列表接口"""
    # 创建测试分类
    create_test_category(db_session)
    db_session.commit()

    # 请求分类列表
    response = test_client.get(f"{BASE_API_URL}/list", headers=admin_headers)
    
    # 验证响应
    assert response.status_code == 200
    data = response.json().get("data")
    assert data["total"] > 0
    assert len(data["items"]) > 0

def test_read_single_category(test_client: TestClient, db_session: Session, admin_headers: Dict[str, str]):
    """测试获取单个附件分类接口"""
    # 创建测试分类
    category = create_test_category(db_session)
    db_session.commit()

    # 请求分类详情
    response = test_client.get(f"{BASE_API_URL}/{category.id}", headers=admin_headers)

    # 验证响应
    assert response.status_code == 200
    data = response.json().get("data")
    assert data["name"] == category.name
    assert data["code"] == category.code

def test_create_category(test_client: TestClient, db_session: Session, admin_headers: Dict[str, str]):
    """测试创建附件分类接口"""
    # 准备创建数据
    category_data = generate_test_category_data()
    
    # 发送创建请求
    response = test_client.post(
        f"{BASE_API_URL}/create", 
        json=category_data, 
        headers=admin_headers
    )

    # 验证响应
    assert response.status_code == 200
    data = response.json().get("data")
    assert "insert_id" in data

    # 验证数据库
    db_session.commit()
    category = crud_sys_attachment_category.get(db_session, id=data["insert_id"])
    assert category is not None
    assert category.name == category_data["name"]

def test_update_category(test_client: TestClient, db_session: Session, admin_headers: Dict[str, str]):
    """测试更新附件分类接口"""
    # 创建测试分类
    category = create_test_category(db_session)
    db_session.commit()
    db_session.refresh(category)

    # 准备更新数据
    update_data = {
        "id": category.id,
        "name": f"更新分类{random.randint(1000,9999)}",
        "code": f"updated{random.randint(1000,9999)}",
        "max_size": 2048,
        "extensions": "jpg,png,gif",
        "mime_types": "image/jpeg,image/png,image/gif",
        "status": "hidden"
    }
    
    # 创建更新模型
    update_model = SysAttachmentCategoryUpdate(**update_data)

    # 发送更新请求
    response = test_client.put(
        f"{BASE_API_URL}/update/{category.id}",
        json=update_model.model_dump(exclude_unset=True),
        headers=admin_headers
    )

    # 验证响应
    assert response.status_code == 200
    data = response.json().get("data")
    assert data["name"] == update_data["name"]

    # 验证数据库
    db_session.commit()
    updated_category = crud_sys_attachment_category.get(db_session, id=category.id)
    db_session.refresh(updated_category)
    assert updated_category is not None
    assert updated_category.name == update_data["name"]

def test_delete_category(test_client: TestClient, db_session: Session, admin_headers: Dict[str, str]):
    """测试删除附件分类接口"""
    # 创建测试分类
    category = create_test_category(db_session)
    db_session.commit()
    db_session.refresh(category)
    
    # 发送删除请求
    response = test_client.delete(
        f"{BASE_API_URL}/delete/{category.id}", 
        headers=admin_headers
    )
    
    # 验证响应
    assert response.status_code == 200
    
    # 验证数据库
    db_session.commit()
    with pytest.raises(exc.ObjectDeletedError):
        crud_sys_attachment_category.get(db_session, id=category.id)
