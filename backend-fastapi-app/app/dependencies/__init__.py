"""
依赖注入模块
提供数据库会话、认证等 FastAPI 依赖
"""

# 同步数据库依赖
# 认证依赖
from app.dependencies.auth import (
    get_current_admin,
    get_current_user,
    get_optional_admin,
    require_permissions,
)
from app.dependencies.database import (
    DatabaseConnectionError,
    DatabaseManager,
    check_db_connection,
    db_manager,
    db_session,
    db_session_safe,
    get_db,
    init_database,
)

# 异步数据库依赖
from app.dependencies.database_async import (
    AsyncBaseRepository,
    AsyncDatabaseError,
    check_async_db_connection,
    close_async_db,
    get_async_db,
    get_async_engine,
    get_async_session_factory,
)

__all__ = [
    # 同步数据库
    "get_db",
    "db_session",
    "db_session_safe",
    "db_manager",
    "DatabaseManager",
    "DatabaseConnectionError",
    "check_db_connection",
    "init_database",
    # 异步数据库
    "get_async_db",
    "get_async_engine",
    "get_async_session_factory",
    "check_async_db_connection",
    "close_async_db",
    "AsyncBaseRepository",
    "AsyncDatabaseError",
    # 认证
    "get_current_admin",
    "get_current_user",
    "get_optional_admin",
    "require_permissions",
]
