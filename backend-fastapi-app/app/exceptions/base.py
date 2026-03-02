"""
业务异常基类定义
"""

from typing import Any

from fastapi import status


class BusinessException(Exception):
    """
    业务异常基类

    Attributes:
        code: 业务错误码
        message: 错误信息
        status_code: HTTP 状态码
        data: 额外数据
    """

    def __init__(
        self,
        code: int = 1000,
        message: str = "Business error",
        status_code: int = status.HTTP_400_BAD_REQUEST,
        data: dict[str, Any] | None = None,
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.data = data or {}
        super().__init__(self.message)


class ValidationError(BusinessException):
    """参数验证错误"""

    def __init__(self, message: str = "Validation error", data: dict[str, Any] | None = None):
        super().__init__(
            code=1001, message=message, status_code=status.HTTP_400_BAD_REQUEST, data=data
        )


class UnauthorizedError(BusinessException):
    """未授权错误"""

    def __init__(self, message: str = "Unauthorized", data: dict[str, Any] | None = None):
        super().__init__(
            code=1002, message=message, status_code=status.HTTP_401_UNAUTHORIZED, data=data
        )


class ForbiddenError(BusinessException):
    """禁止访问错误"""

    def __init__(self, message: str = "Forbidden", data: dict[str, Any] | None = None):
        super().__init__(
            code=1003, message=message, status_code=status.HTTP_403_FORBIDDEN, data=data
        )


class NotFoundError(BusinessException):
    """资源不存在错误"""

    def __init__(self, message: str = "Resource not found", data: dict[str, Any] | None = None):
        super().__init__(
            code=1004, message=message, status_code=status.HTTP_404_NOT_FOUND, data=data
        )


class ConflictError(BusinessException):
    """资源冲突错误（如重复数据）"""

    def __init__(self, message: str = "Resource conflict", data: dict[str, Any] | None = None):
        super().__init__(
            code=1005, message=message, status_code=status.HTTP_409_CONFLICT, data=data
        )


class DatabaseError(BusinessException):
    """数据库错误"""

    def __init__(self, message: str = "Database error", data: dict[str, Any] | None = None):
        super().__init__(
            code=1006, message=message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, data=data
        )


class RateLimitError(BusinessException):
    """请求频率限制错误"""

    def __init__(self, message: str = "Rate limit exceeded", data: dict[str, Any] | None = None):
        super().__init__(
            code=1007, message=message, status_code=status.HTTP_429_TOO_MANY_REQUESTS, data=data
        )


class ServiceUnavailableError(BusinessException):
    """服务不可用错误"""

    def __init__(self, message: str = "Service unavailable", data: dict[str, Any] | None = None):
        super().__init__(
            code=1008, message=message, status_code=status.HTTP_503_SERVICE_UNAVAILABLE, data=data
        )
