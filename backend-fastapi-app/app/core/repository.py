"""
Repository 兼容层
从 app.repositories.base 导出所有内容，保持向后兼容
"""

# 直接重新导出所有内容，保持向后兼容
from app.repositories.base import (
    # Repository 基类
    BaseRepository,
    CreateSchemaType,
    # 类型变量
    ModelType,
    # 查询构建器
    QueryBuilder,
    # 异常
    RepositoryError,
    UpdateSchemaType,
    create_repository_class,
    # 工具函数
    get_repository,
)

# 别名，保持兼容性
EnhancedRepository = BaseRepository

__all__ = [
    "BaseRepository",
    "CreateSchemaType",
    "EnhancedRepository",
    "ModelType",
    "QueryBuilder",
    "RepositoryError",
    "UpdateSchemaType",
    "create_repository_class",
    "get_repository",
]
