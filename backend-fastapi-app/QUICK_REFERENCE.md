# 架构快速参考

## 目录

1. [Repository 层](#repository-层)
2. [Service 层](#service-层)
3. [API 层](#api-层)
4. [数据库会话](#数据库会话)
5. [日志](#日志)
6. [测试](#测试)

---

## Repository 层

### 基础使用

```python
from app.repositories.base import BaseRepository
from app.dependencies.database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends

# 创建 Repository 实例
repo = BaseRepository(MyModel)

def get_items(db: Session = Depends(get_db)):
    # 基础 CRUD
    item = repo.get(db, id=1)
    items = repo.get_multi(db, page=1, per_page=10)
    total = repo.count(db)
    
    # 搜索和排序
    items = repo.get_multi(db, search="keyword", order_by="created_at_desc")
    
    # 自定义查询
    query = repo.query(db)
    items = query.filter(MyModel.status == "active").search("keyword").order_by("-created_at").paginate(1, 10).all()
```

### 自定义 Repository

```python
class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    DEFAULT_SEARCH_FIELDS = ['username', 'email', 'nickname']
    DEFAULT_UNIQUE_FIELDS = ['username', 'email', 'mobile']
    
    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        return self.get_by(db, username=username)
    
    def get_active_users(self, db: Session) -> List[User]:
        return self.query(db).filter(User.status == "active").all()

# 单例实例
user_repo = UserRepository()
```

### 动态创建 Repository

```python
from app.repositories.base import create_repository_class

UserRepo = create_repository_class(
    User,
    search_fields=['username', 'email'],
    unique_fields=['username']
)
repo = UserRepo()
```

---

## Service 层

### 基础使用

```python
from app.services.base import BaseService, Transactional
from app.modules.admin.sys_admin.repositories.sys_admin import sys_admin_repo

class AdminService(BaseService[Admin, AdminCreate, AdminUpdate]):
    def __init__(self):
        super().__init__(sys_admin_repo)
    
    def authenticate(self, db: Session, username: str, password: str):
        admin = self._repo.get_by_username(db, username)
        if admin and admin.check_password(password):
            return admin
        return None
    
    @Transactional()  # 自动事务管理
    def create_with_logs(self, db: Session, data: dict):
        admin = self.create(db, data)
        # 创建日志记录...
        return admin

# 使用
service = AdminService()
```

### 简化版 CRUD Service

```python
from app.services.base import CrudService

class UserService(CrudService[User, UserCreate, UserUpdate]):
    DEFAULT_SEARCH_FIELDS = ['username', 'email']
    DEFAULT_UNIQUE_FIELDS = ['username', 'email']

# 自动创建 Repository
service = UserService(User)
```

---

## API 层

### 基础路由

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.dependencies.auth import get_current_admin, CurrentAdmin

router = APIRouter(prefix="/items", tags=["items"])

@router.get("/list")
def list_items(
    page: int = 1,
    per_page: int = 10,
    db: Session = Depends(get_db),
    current_admin: CurrentAdmin = None
):
    items = service.get_multi(db, page=page, per_page=per_page)
    return success_response({
        "items": [item.to_dict() for item in items],
        "total": service.count(db)
    })
```

### 使用分页参数

```python
from app.services.pagination import SearchParams, PaginatedResponse

@router.get("/list")
def list_items(
    params: SearchParams = Depends(),
    db: Session = Depends(get_db)
):
    items, total = service.get_admin_list(
        db,
        page=params.page,
        per_page=params.per_page,
        search=params.search,
        orderby=params.order_by
    )
    return PaginatedResponse.create(items, total, params.page, params.per_page)
```

---

## 数据库会话

### FastAPI Depends

```python
from app.dependencies.database import get_db
from sqlalchemy.orm import Session

def get_items(db: Session = Depends(get_db)):
    return repo.get_multi(db)
```

### 上下文管理器

```python
from app.dependencies.database import db_session, db_session_safe

# 基础上下文
with db_session() as db:
    items = repo.get_multi(db)
    repo.create(db, data)

# 带重试机制
with db_session_safe(max_retries=3) as db:
    if db is not None:
        repo.create(db, data)
```

### 异步会话

```python
from app.dependencies.database_async import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession

@router.get("/items")
async def get_items(db: AsyncSession = Depends(get_async_db)):
    repo = AsyncBaseRepository(MyModel)
    items = await repo.get_multi(db)
    return items
```

---

## 日志

### 基础使用

```python
from app.core.logging import get_logger

logger = get_logger(__name__)

logger.debug("Debug message")
logger.info("Info message", extra={"user_id": 123})
logger.warning("Warning message")
logger.error("Error message", exc_info=True)
```

### 上下文绑定

```python
# 绑定上下文
request_logger = logger.bind(request_id="abc-123", user_id=456)

# 后续日志自动包含上下文
request_logger.info("Processing request")  # 包含 request_id 和 user_id
request_logger.info("Request completed")   # 包含 request_id 和 user_id
```

---

## 测试

### 基础测试

```python
# tests/test_example.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

def test_get_items(client: TestClient, db_session: Session):
    response = client.get("/api/items/list")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
```

### 认证测试

```python
from tests.conftest import create_test_admin, get_auth_headers

def test_protected_route(client: TestClient, db_session: Session):
    # 创建测试用户
    create_test_admin(db_session, username="test", password="test123")
    
    # 获取认证头
    headers = get_auth_headers(client, "test", "test123")
    
    # 访问受保护接口
    response = client.get("/api/admin/admin/list", headers=headers)
    assert response.status_code == 200
```

### Repository 测试

```python
def test_repository_create(db_session: Session):
    from app.repositories.base import BaseRepository
    
    repo = BaseRepository(MyModel)
    item = repo.create(db_session, {"name": "Test"})
    
    assert item.id is not None
    assert item.name == "Test"
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_auth.py

# 带覆盖率
pytest --cov=app tests/

# 详细输出
pytest -v
```

---

## 常用导入速查

```python
# Repository
from app.repositories.base import BaseRepository, create_repository_class

# Service
from app.services.base import BaseService, CrudService, Transactional, service_transaction

# 分页
from app.services.pagination import PaginationParams, SearchParams, PaginatedResponse

# 数据库
from app.dependencies.database import get_db, db_session, db_session_safe, DatabaseManager
from app.dependencies.database_async import get_async_db, AsyncBaseRepository

# 认证
from app.dependencies.auth import get_current_admin, get_current_user, CurrentAdmin, CurrentUser

# 日志
from app.core.logging import get_logger
from app.utils.log_utils import logger  # 兼容旧代码

# 异常
from app.exceptions import NotFoundError, ConflictError, UnauthorizedError, BusinessException

# 响应
from app.utils.responses import success_response, error_response
```
