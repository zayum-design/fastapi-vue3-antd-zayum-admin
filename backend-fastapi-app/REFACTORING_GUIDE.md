# 代码重构指南

本文档介绍了本次优化的主要内容及如何使用新特性。

## 1. 异常处理（已优化）

### 新特性
- 统一的业务异常体系
- 自动异常处理器注册
- 结构化的错误响应

### 使用示例

```python
from fastapi import APIRouter
from sqlalchemy.orm import Session
from app.exceptions import NotFoundError, ValidationError, ConflictError
from app.dependencies.database import get_db

router = APIRouter()

@router.get("/items/{item_id}")
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        # 自动返回 404 响应
        raise NotFoundError(f"Item {item_id} not found")
    return item

@router.post("/items")
def create_item(item_data: ItemCreate, db: Session = Depends(get_db)):
    # 参数验证错误
    if item_data.price < 0:
        raise ValidationError("Price must be positive")
    
    # 检查重复
    existing = db.query(Item).filter(Item.name == item_data.name).first()
    if existing:
        raise ConflictError(f"Item with name '{item_data.name}' already exists")
    
    # ...
```

### 可用的异常类型

| 异常类 | HTTP 状态码 | 用途 |
|--------|------------|------|
| `BusinessException` | 400 | 通用业务异常 |
| `ValidationError` | 400 | 参数验证错误 |
| `UnauthorizedError` | 401 | 未授权 |
| `ForbiddenError` | 403 | 禁止访问 |
| `NotFoundError` | 404 | 资源不存在 |
| `ConflictError` | 409 | 资源冲突 |
| `DatabaseError` | 500 | 数据库错误 |
| `RateLimitError` | 429 | 请求频率限制 |

## 2. Repository 模式（新增）

### 新特性
- 通用 BaseRepository 基类
- 链式查询构建器
- 自动唯一性验证
- 批量操作支持

### 使用示例

#### 基础使用

```python
from app.repositories.base import BaseRepository
from app.modules.admin.sys_user.models.sys_user import SysUser
from app.modules.admin.sys_user.schemas.sys_user import SysUserCreate, SysUserUpdate

class SysUserRepository(BaseRepository[SysUser, SysUserCreate, SysUserUpdate]):
    def __init__(self):
        super().__init__(SysUser)
        # 设置可搜索字段
        self.set_searchable_fields(['username', 'email', 'nickname'])
        # 设置唯一字段（自动验证）
        self.set_unique_fields(['username', 'email'])
    
    def get_by_username(self, db: Session, username: str):
        return self.get_by(db, username=username)

# 创建全局实例
sys_user_repo = SysUserRepository()

# 在路由中使用
@router.get("/users")
def list_users(
    search: str = None,
    page: int = 1,
    db: Session = Depends(get_db)
):
    return sys_user_repo.get_multi(
        db, 
        page=page, 
        per_page=20, 
        search=search,
        order_by=["-created_at"]
    )

@router.post("/users")
def create_user(user_in: SysUserCreate, db: Session = Depends(get_db)):
    # 自动检查 username 和 email 唯一性
    return sys_user_repo.create(db, user_in)
```

#### 链式查询构建器

```python
# 复杂查询
users = (
    sys_user_repo.query(db)
    .filter_by(status='active')
    .search('john')
    .order_by('-created_at', 'username')
    .paginate(page=1, per_page=10)
    .all()
)

# 条件查询
active_admins = (
    sys_user_repo.query(db)
    .filter(SysUser.role == 'admin', SysUser.status == 'active')
    .all()
)

# 统计
count = sys_user_repo.query(db).filter_by(status='active').count()
exists = sys_user_repo.query(db).filter_by(email='test@example.com').exists()
```

## 3. 日志记录（已优化）

### 新特性
- 结构化日志（JSON 格式）
- 带上下文的日志记录
- 颜色化的控制台输出

### 使用示例

```python
from app.utils.log_utils import logger, get_logger

# 基础使用
logger.info("User logged in")
logger.error("Database connection failed")

# 结构化日志（带额外上下文）
logger.info(
    "User action",
    extra={
        "user_id": 123,
        "action": "create_post",
        "ip": "192.168.1.1"
    }
)

# 使用带上下文的 logger
user_logger = get_logger(extra={"module": "user_service"})
user_logger.info("Processing user request")  # 自动包含 module=user_service

# 设置日志级别
from app.utils.log_utils import set_log_level
set_log_level("DEBUG")  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## 4. 配置管理（已优化）

### 新特性
- 多环境配置支持
- 类型安全的配置项
- 自动版本号读取

### 使用示例

```python
from app.core.config import settings, Environment

# 访问配置
print(settings.DATABASE_URL)
print(settings.VERSION)

# 检查环境
if settings.ENV == Environment.DEVELOPMENT:
    print("Running in development mode")

# 开发环境自动开启调试
if settings.DEBUG:
    print("Debug mode enabled")
```

### 环境变量

```bash
# 设置环境
export ENV=production  # development, testing, production

# 或使用 .env 文件
# .env.development
ENV=development
DEBUG=true
LOG_LEVEL=DEBUG

# .env.production
ENV=production
DEBUG=false
LOG_LEVEL=WARNING
```

## 5. 异步数据库（新增）

### 安装依赖

```bash
pip install asyncmy
```

### 使用示例

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.dependencies.database_async import get_async_db, AsyncBaseRepository
from app.modules.admin.sys_user.models.sys_user import SysUser

router = APIRouter()

# 创建异步 Repository
sys_user_async_repo = AsyncBaseRepository[SysUser, SysUserCreate, SysUserUpdate](SysUser)

@router.get("/users")
async def list_users(db: AsyncSession = Depends(get_async_db)):
    return await sys_user_async_repo.get_multi(db, skip=0, limit=100)

@router.post("/users")
async def create_user(
    user_in: SysUserCreate,
    db: AsyncSession = Depends(get_async_db)
):
    return await sys_user_async_repo.create(db, user_in)

@router.get("/users/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_async_db)):
    user = await sys_user_async_repo.get(db, user_id)
    if not user:
        raise NotFoundError(f"User {user_id} not found")
    return user
```

## 6. 代码检查工具

### 安装

```bash
pip install ruff mypy pytest
```

### 使用

```bash
# 代码格式化
ruff format .

# 代码检查
ruff check .

# 自动修复问题
ruff check . --fix

# 类型检查
mypy app

# 运行测试
pytest
```

### 配置

所有配置在 `pyproject.toml` 中：

```toml
[tool.ruff]
target-version = "py311"
line-length = 100

[tool.mypy]
strict = true
python_version = "3.11"

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
```

## 7. 迁移指南

### 从旧 CRUD 迁移到新 Repository

**旧代码：**

```python
# app/modules/admin/sys_admin/crud/sys_admin.py
class CRUDSysAdmin:
    def get(self, db: Session, id: int):
        return db.query(SysAdmin).filter(SysAdmin.id == id).first()
    
    def create(self, db: Session, obj_in):
        db_obj = SysAdmin(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

crud_sys_admin = CRUDSysAdmin()
```

**新代码：**

```python
# app/modules/admin/sys_admin/crud/sys_admin_v2.py
from app.repositories.base import BaseRepository

class SysAdminRepository(BaseRepository[SysAdmin, SysAdminCreate, SysAdminUpdate]):
    def __init__(self):
        super().__init__(SysAdmin)
        self.set_searchable_fields(['username', 'email', 'nickname'])
        self.set_unique_fields(['username', 'email'])

sys_admin_repo = SysAdminRepository()

# 兼容层（保持旧接口）
class CRUDSysAdmin:
    def get(self, db: Session, id: int):
        return sys_admin_repo.get(db, id)
    
    def create(self, db: Session, obj_in):
        return sys_admin_repo.create(db, obj_in)
    # ... 其他方法

crud_sys_admin = CRUDSysAdmin()
```

### 从旧日志迁移到新日志

**旧代码：**

```python
from app.utils.log_utils import logger

logger.info(f"User {username} logged in from {ip}")
logger.error("Failed to connect to database")
```

**新代码：**

```python
from app.utils.log_utils import logger

# 使用结构化日志
logger.info(
    "User logged in",
    extra={"username": username, "ip": ip}
)

logger.error(
    "Database connection failed",
    extra={"host": db_host, "retry_count": retry_count}
)
```

## 8. 最佳实践

### 异常处理

```python
# ✅ 好的做法 - 使用特定异常
raise NotFoundError(f"User {user_id} not found")

# ❌ 避免 - 使用通用 HTTPException
raise HTTPException(status_code=404, detail="User not found")
```

### Repository 使用

```python
# ✅ 好的做法 - 使用 Repository 方法
user = sys_user_repo.get(db, user_id)

# ❌ 避免 - 直接查询
db.query(SysUser).filter(SysUser.id == user_id).first()
```

### 日志记录

```python
# ✅ 好的做法 - 结构化日志
logger.info("Order created", extra={"order_id": order_id, "amount": amount})

# ❌ 避免 - 字符串拼接
logger.info(f"Order {order_id} created with amount {amount}")
```

## 9. 性能建议

1. **数据库查询**
   - 使用 `selectinload` 预加载关联数据
   - 批量操作使用 `bulk_create` 和 `bulk_delete`
   - 分页查询限制最大条数（默认 100）

2. **缓存**
   - 考虑添加 Redis 缓存层
   - 缓存查询结果和会话数据

3. **异步**
   - I/O 密集型操作使用异步
   - 注意异步和同步代码的混合使用

## 10. 待办清单

- [x] 统一异常处理
- [x] 日志规范
- [x] BaseRepository 基类
- [x] 配置分级
- [x] 类型注解
- [x] 异步数据库支持
- [x] 代码检查工具配置
- [ ] 所有 CRUD 迁移到新 Repository
- [ ] 添加缓存层
- [ ] 完善测试覆盖
