import random
from typing import Generator, Dict, Any
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, exc
from sqlalchemy.sql import text
import os
from pathlib import Path

from app.main import app
from app.crud.sys_attachment import crud_sys_attachment
from app.dependencies.database import get_db
from app.core.security import create_access_token
from app.models.sys_attachment import SysAttachment

# Constants
ADMIN_USER_ID = 1
BASE_API_URL = "/api/admin/upload"
TEST_FILE_DIR = Path(__file__).parent.parent.parent / "test_files"
TEST_FILE_DIR.mkdir(exist_ok=True)

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

@pytest.fixture
def test_file() -> Generator[str, None, None]:
    """创建测试文件"""
    test_file_path = str(TEST_FILE_DIR / "test_upload.txt")
    with open(test_file_path, "w") as f:
        f.write("This is a test file for upload")
    yield test_file_path
    if os.path.exists(test_file_path):
        os.remove(test_file_path)

def test_upload_file(test_client: TestClient, db_session: Session, admin_headers: Dict[str, str], test_file: str):
    """测试文件上传接口"""
    # 准备上传数据
    files = {"file": ("test_upload.txt", open(test_file, "rb"), "text/plain")}
    data = {"category_id": 1}
    
    # 发送上传请求
    response = test_client.post(
        f"{BASE_API_URL}",
        files=files,
        data=data,
        headers=admin_headers
    )

    # 验证响应
    assert response.status_code == 200
    data = response.json().get("data")
    assert "image_url" in data
    assert data["image_url"].startswith("/uploads/")

    # 验证数据库
    db_session.commit()
    attachment = crud_sys_attachment.get(db_session, id=data["id"])
    assert attachment is not None
    assert attachment.name == "test_upload.txt"

def test_upload_invalid_file(test_client: TestClient, admin_headers: Dict[str, str]):
    """测试上传无效文件"""
    # 准备上传数据
    files = {"file": ("test_upload.txt", b"", "text/plain")}
    data = {"category_id": 1}
    
    # 发送上传请求
    response = test_client.post(
        f"{BASE_API_URL}",
        files=files,
        data=data,
        headers=admin_headers
    )

    # 验证响应
    assert response.status_code == 200
    assert "文件内容不能为空" in response.json().get("msg")

def test_upload_without_category(test_client: TestClient, admin_headers: Dict[str, str], test_file: str):
    """测试上传文件未指定分类"""
    # 准备上传数据
    files = {"file": ("test_upload.txt", open(test_file, "rb"), "text/plain")}
    
    # 发送上传请求
    response = test_client.post(
        f"{BASE_API_URL}",
        files=files,
        headers=admin_headers
    )

    # 验证响应
    assert response.status_code == 200
    assert "请选择文件分类" in response.json().get("msg")
