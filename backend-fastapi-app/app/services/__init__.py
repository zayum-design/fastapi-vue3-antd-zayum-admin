"""
Service 层模块
提供业务逻辑处理

架构分层：
- API Layer (Routes): 处理 HTTP 请求/响应
- Service Layer: 处理业务逻辑
- Repository Layer: 处理数据访问
- Model Layer: 数据模型定义
"""

from app.services.base import (
    BaseService,
    ServiceError,
    Transactional,
    service_transaction,
)

__all__ = [
    "BaseService",
    "ServiceError",
    "Transactional",
    "service_transaction",
]
