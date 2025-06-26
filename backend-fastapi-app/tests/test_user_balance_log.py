import random
from typing import Generator, Dict, Any
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, exc
from sqlalchemy.sql import text

from app.main import app
from app.crud.sys_user_balance_log import crud_sys_user_balance_log
from app.schemas.sys_user_balance_log import SysUserBalanceLogCreate, SysUserBalanceLogUpdate
from app.dependencies.database import get_db
from app.core.security import create_access_token
from app.models.sys_user_balance_log import SysUserBalanceLog

# Constants
ADMIN_USER_ID = 1
BASE_API_URL = "/api/admin/user_balance_log"

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

def generate_test_balance_log_data() -> Dict[str, Any]:
    """生成测试用户余额日志数据"""
    rand = random.randint(1000, 9999)
    return {
        "user_id": 1,
        "amount": "100.00",  # 改为字符串格式
        "before": "0.00",    # 改为字符串格式
        "after": "100.00",   # 改为字符串格式
        "memo": f"测试余额变更{rand}",
        "type": "recharge",
        "admin_id": 1,       # 添加必填字段
        "create_time": "2025-01-01 00:00:00"  # 添加必填字段
    }

def create_test_balance_log(db: Session) -> SysUserBalanceLog:
    """创建测试用户余额日志并返回"""
    log_data = SysUserBalanceLogCreate(**generate_test_balance_log_data())
    return crud_sys_user_balance_log.create(db, obj_in=log_data)

def test_read_balance_log_list(test_client: TestClient, db_session: Session, admin_headers: Dict[str, str]):
    """测试获取用户余额日志列表接口"""
    # 创建测试日志
    log = create_test_balance_log(db_session)
    db_session.commit()

    # 请求日志列表
    response = test_client.get(f"{BASE_API_URL}", headers=admin_headers)  # 修正路由
    
    # 验证响应
    assert response.status_code == 200
    data = response.json().get("data", {})
    assert isinstance(data, list)
    assert len(data) > 0

def test_read_single_balance_log(test_client: TestClient, db_session: Session, admin_headers: Dict[str, str]):
    """测试获取单个用户余额日志接口"""
    # 创建测试日志
    log = create_test_balance_log(db_session)
    db_session.commit()

    # 请求日志详情
    response = test_client.get(f"{BASE_API_URL}/{log.id}", headers=admin_headers)

    # 验证响应
    assert response.status_code == 200
    data = response.json().get("data")
    assert data["user_id"] == log.user_id
    assert float(data["amount"]) == log.amount

def test_create_balance_log(test_client: TestClient, db_session: Session, admin_headers: Dict[str, str]):
    """测试创建用户余额日志接口"""
    # 准备创建数据
    log_data = generate_test_balance_log_data()
    
    # 发送创建请求
    response = test_client.post(
        f"{BASE_API_URL}/create", 
        json=log_data, 
        headers=admin_headers
    )

    # 验证响应
    assert response.status_code == 200
    data = response.json().get("data")
    assert "insert_id" in data

    # 验证数据库
    db_session.commit()
    log = crud_sys_user_balance_log.get(db_session, id=data["insert_id"])
    assert log is not None
    assert log.memo == log_data["memo"]

def test_update_balance_log(test_client: TestClient, db_session: Session, admin_headers: Dict[str, str]):
    """测试更新用户余额日志接口"""
    # 创建测试日志
    log = create_test_balance_log(db_session)
    db_session.commit()
    db_session.refresh(log)

    # 准备更新数据
    update_data = {
        "id": log.id,
        "user_id": log.user_id,
        "amount": 200.00,
        "before": log.before,
        "after": log.before + 200.00,
        "memo": f"更新余额变更{random.randint(1000,9999)}",
        "type": "adjust"
    }
    
    # 创建更新模型
    update_model = SysUserBalanceLogUpdate(**update_data)

    # 发送更新请求
    response = test_client.put(
        f"{BASE_API_URL}/update/{log.id}",
        json=update_model.model_dump(exclude_unset=True),
        headers=admin_headers
    )

    # 验证响应
    assert response.status_code == 200
    data = response.json().get("data")
    assert float(data["amount"]) == update_data["amount"]

    # 验证数据库
    db_session.commit()
    updated_log = crud_sys_user_balance_log.get(db_session, id=log.id)
    db_session.refresh(updated_log)
    assert updated_log is not None
    assert updated_log.amount == update_data["amount"]

def test_delete_balance_log(test_client: TestClient, db_session: Session, admin_headers: Dict[str, str]):
    """测试删除用户余额日志接口"""
    # 创建测试日志
    log = create_test_balance_log(db_session)
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
        crud_sys_user_balance_log.get(db_session, id=log.id)
