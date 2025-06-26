import random
from typing import Generator, Dict, Any
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, exc
from sqlalchemy.sql import text

from app.main import app
from app.crud.sys_attachment import crud_sys_attachment
from app.schemas.sys_attachment import SysAttachmentCreate, SysAttachmentUpdate
from app.dependencies.database import get_db
from app.core.security import create_access_token
from app.models.sys_attachment import SysAttachment

# Constants
ADMIN_USER_ID = 1
BASE_API_URL = "/api/admin/attachment"

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

def generate_test_attachment_data() -> Dict[str, Any]:
    """生成测试附件数据"""
    rand = random.randint(1000, 9999)
    return {
        "category_id": 1,
        "name": f"测试附件{rand}",
        "path": f"/uploads/test{rand}.jpg",
        "mime_type": "image/jpeg",
        "size": 1024,
        "width": 800,
        "height": 600,
        "status": "normal"
    }

def create_test_attachment(db: Session) -> SysAttachment:
    """创建测试附件并返回"""
    attachment_data = SysAttachmentCreate(**generate_test_attachment_data())
    return crud_sys_attachment.create(db, obj_in=attachment_data)

def test_read_attachment_list(test_client: TestClient, db_session: Session, admin_headers: Dict[str, str]):
    """测试获取附件列表接口"""
    # 创建测试附件
    create_test_attachment(db_session)
    db_session.commit()

    # 请求附件列表
    response = test_client.get(f"{BASE_API_URL}/list", headers=admin_headers)
    
    # 验证响应
    assert response.status_code == 200
    data = response.json().get("data")
    assert data["total"] > 0
    assert len(data["items"]) > 0

def test_read_single_attachment(test_client: TestClient, db_session: Session, admin_headers: Dict[str, str]):
    """测试获取单个附件接口"""
    # 创建测试附件
    attachment = create_test_attachment(db_session)
    db_session.commit()

    # 请求附件详情
    response = test_client.get(f"{BASE_API_URL}/{attachment.id}", headers=admin_headers)

    # 验证响应
    assert response.status_code == 200
    data = response.json().get("data")
    assert data["name"] == attachment.name
    assert data["path"] == attachment.path

def test_create_attachment(test_client: TestClient, db_session: Session, admin_headers: Dict[str, str]):
    """测试创建附件接口"""
    # 准备创建数据
    attachment_data = generate_test_attachment_data()
    
    # 发送创建请求
    response = test_client.post(
        f"{BASE_API_URL}/create", 
        json=attachment_data, 
        headers=admin_headers
    )

    # 验证响应
    assert response.status_code == 200
    data = response.json().get("data")
    assert "insert_id" in data

    # 验证数据库
    db_session.commit()
    attachment = crud_sys_attachment.get(db_session, id=data["insert_id"])
    assert attachment is not None
    assert attachment.name == attachment_data["name"]

def test_update_attachment(test_client: TestClient, db_session: Session, admin_headers: Dict[str, str]):
    """测试更新附件接口"""
    # 创建测试附件
    attachment = create_test_attachment(db_session)
    db_session.commit()
    db_session.refresh(attachment)

    # 准备更新数据
    update_data = {
        "id": attachment.id,
        "category_id": 2,
        "name": f"更新附件{random.randint(1000,9999)}",
        "path": f"/uploads/updated{random.randint(1000,9999)}.jpg",
        "mime_type": "image/png",
        "size": 2048,
        "width": 1024,
        "height": 768,
        "status": "hidden"
    }
    
    # 创建更新模型
    update_model = SysAttachmentUpdate(**update_data)

    # 发送更新请求
    response = test_client.put(
        f"{BASE_API_URL}/update/{attachment.id}",
        json=update_model.model_dump(exclude_unset=True),
        headers=admin_headers
    )

    # 验证响应
    assert response.status_code == 200
    data = response.json().get("data")
    assert data["name"] == update_data["name"]

    # 验证数据库
    db_session.commit()
    updated_attachment = crud_sys_attachment.get(db_session, id=attachment.id)
    db_session.refresh(updated_attachment)
    assert updated_attachment is not None
    assert updated_attachment.name == update_data["name"]

def test_delete_attachment(test_client: TestClient, db_session: Session, admin_headers: Dict[str, str]):
    """测试删除附件接口"""
    # 创建测试附件
    attachment = create_test_attachment(db_session)
    db_session.commit()
    db_session.refresh(attachment)
    
    # 发送删除请求
    response = test_client.delete(
        f"{BASE_API_URL}/delete/{attachment.id}", 
        headers=admin_headers
    )
    
    # 验证响应
    assert response.status_code == 200
    
    # 验证数据库
    db_session.commit()
    with pytest.raises(exc.ObjectDeletedError):
        crud_sys_attachment.get(db_session, id=attachment.id)
