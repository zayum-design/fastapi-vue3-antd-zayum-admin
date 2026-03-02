"""
业务异常模块
提供统一的异常处理体系
"""

from .base import (
    BusinessException,
    ConflictError,
    DatabaseError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    ServiceUnavailableError,
    UnauthorizedError,
    ValidationError,
)

__all__ = [
    "BusinessException",
    "ConflictError",
    "DatabaseError",
    "ForbiddenError",
    "NotFoundError",
    "RateLimitError",
    "ServiceUnavailableError",
    "UnauthorizedError",
    "ValidationError",
]
