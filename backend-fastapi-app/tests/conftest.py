import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from app.main import app
from app.dependencies.database import SessionLocal, get_db
from app.core.security import create_access_token
from app.models.sys_user import SysUser
from fastapi_babel import Babel
from contextvars import ContextVar

_ = lambda x: x
context_var: ContextVar[Babel] = ContextVar("gettext")

@pytest.fixture(scope="module")
def test_client():
    """创建测试客户端"""
    context_var.set(_)
    with TestClient(app) as client:
        yield client

@pytest.fixture(scope="function")
def db_session():
    """获取数据库会话"""
    # 检查数据库连接
    context_var.set(_)
    db = SessionLocal()
    try:
        # 测试数据库连接
        db.execute(text("SELECT 1"))
        yield db
    except Exception as e:
        pytest.fail(f"数据库连接失败: {str(e)}")
    finally:
        db.rollback()
        db.close()

@pytest.fixture(scope="session", autouse=True)
def babel(request):
    """配置 fastapi_babel"""
    from app.core.config import settings
    app.babel = Babel(settings)
    return app.babel
