# 数据库查询优化建议

## 1. 添加索引建议

### SysUser 表
```sql
-- 为常用查询条件添加索引
CREATE INDEX idx_sys_user_username ON sys_user(username);
CREATE INDEX idx_sys_user_email ON sys_user(email);
CREATE INDEX idx_sys_user_mobile ON sys_user(mobile);
CREATE INDEX idx_sys_user_status ON sys_user(status);
CREATE INDEX idx_sys_user_created_at ON sys_user(created_at);
CREATE INDEX idx_sys_user_login_time ON sys_user(login_time);
CREATE INDEX idx_sys_user_join_ip ON sys_user(join_ip);

-- 复合索引（用于排序+过滤）
CREATE INDEX idx_sys_user_status_created_at ON sys_user(status, created_at DESC);
```

### SysAdmin 表
```sql
CREATE INDEX idx_sys_admin_username ON sys_admin(username);
CREATE INDEX idx_sys_admin_group_id ON sys_admin(group_id);
CREATE INDEX idx_sys_admin_status ON sys_admin(status);
CREATE INDEX idx_sys_admin_login_time ON sys_admin(login_time);
```

### SysAdminLog 表
```sql
CREATE INDEX idx_sys_admin_log_admin_id ON sys_admin_log(admin_id);
CREATE INDEX idx_sys_admin_log_created_at ON sys_admin_log(created_at);
CREATE INDEX idx_sys_admin_log_title ON sys_admin_log(title);
-- 复合索引用于时间范围查询
CREATE INDEX idx_sys_admin_log_created_at_admin_id ON sys_admin_log(created_at, admin_id);
```

### SysAttachment 表
```sql
CREATE INDEX idx_sys_attachment_admin_id ON sys_attachment(admin_id);
CREATE INDEX idx_sys_attachment_user_id ON sys_attachment(user_id);
CREATE INDEX idx_sys_attachment_cat_id ON sys_attachment(cat_id);
CREATE INDEX idx_sys_attachment_sha1 ON sys_attachment(sha1);
CREATE INDEX idx_sys_attachment_created_at ON sys_attachment(created_at);
```

## 2. 查询优化示例

### 使用 exists() 替代 join 进行存在性检查
```python
# 优化前
existing = db.query(SysUser).filter(SysUser.username == username).first()

# 优化后（只需要检查是否存在）
from sqlalchemy import exists
stmt = exists().where(SysUser.username == username)
existing = db.query(stmt).scalar()
```

### 使用批量操作减少数据库往返
```python
# 优化前（多次查询）
for user_id in user_ids:
    user = db.query(SysUser).filter(SysUser.id == user_id).first()

# 优化后（单次查询）
users = db.query(SysUser).filter(SysUser.id.in_(user_ids)).all()
users_dict = {user.id: user for user in users}
```

### 使用 eager loading 避免 N+1 查询
```python
# 优化前（N+1 查询）
users = db.query(SysUser).all()
for user in users:
    group = db.query(SysAdminGroup).filter(SysAdminGroup.id == user.group_id).first()

# 优化后（eager loading）
from sqlalchemy.orm import joinedload
users = db.query(SysUser).options(joinedload(SysUser.group)).all()
```

### 使用 selectinload 避免多次查询关联数据
```python
from sqlalchemy.orm import selectinload

users = db.query(SysUser).options(
    selectinload(SysUser.logs)
).all()
```

## 3. 分页查询优化

### 使用游标分页（适用于大数据集）
```python
def get_users_cursor(db: Session, last_id: int = None, limit: int = 10):
    query = db.query(SysUser)
    if last_id:
        query = query.filter(SysUser.id > last_id)
    return query.order_by(SysUser.id).limit(limit).all()
```

## 4. 缓存策略

### 查询结果缓存
```python
from functools import lru_cache
import hashlib
import pickle

def cache_key_func(query, params):
    """生成缓存键"""
    key_str = str(query) + str(sorted(params.items()))
    return hashlib.md5(key_str.encode()).hexdigest()

# 在适当的位置添加缓存装饰器
```

## 5. 数据库连接池配置

### 在 config.py 中优化连接池设置
```python
# 建议配置
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 20,
    'max_overflow': 10,
    'pool_timeout': 30,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
}
```

## 6. 批量插入优化

```python
# 使用 bulk_insert_mappings 进行批量插入
from sqlalchemy import insert

def batch_insert_users(db: Session, users_data: List[Dict]):
    stmt = insert(SysUser).values(users_data)
    db.execute(stmt)
    db.commit()
```

## 7. 查询分析

### 使用 explain 分析慢查询
```python
from sqlalchemy import text

result = db.execute(text("EXPLAIN ANALYZE SELECT * FROM sys_user WHERE status = 1"))
print(result.fetchall())
```

## 8. 定期维护

### 定期清理过期数据
```python
from datetime import datetime, timedelta

def cleanup_old_logs(db: Session, days: int = 90):
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    db.query(SysAdminLog).filter(
        SysAdminLog.created_at < cutoff_date
    ).delete(synchronize_session=False)
    db.commit()
```

### 定期更新统计信息
```sql
-- PostgreSQL
ANALYZE sys_user;
ANALYZE sys_admin_log;

-- MySQL
ANALYZE TABLE sys_user;
ANALYZE TABLE sys_admin_log;
```
