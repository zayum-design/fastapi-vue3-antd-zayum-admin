"""
API 限流配置
基于 slowapi，提供多种限流策略

如果 slowapi 未安装，将使用空实现（无限制）
"""

from collections.abc import Callable
from typing import Any

from fastapi import FastAPI

from app.core.config import settings
from app.utils.log_utils import logger

# 全局变量声明
limiter: Any = None
RateLimitExceeded: Any = Exception
_rate_limit_exceeded_handler: Any = None
SLOWAPI_AVAILABLE: bool = False


# 尝试导入 slowapi
try:
    from slowapi import Limiter as _Limiter
    from slowapi import _rate_limit_exceeded_handler as _handler
    from slowapi.errors import RateLimitExceeded as _RateLimitExceeded
    from slowapi.util import get_remote_address

    SLOWAPI_AVAILABLE = True
    RateLimitExceeded = _RateLimitExceeded
    _rate_limit_exceeded_handler = _handler

    # 创建限流器实例
    try:
        if settings.CACHE_TYPE == "redis":
            try:
                import redis

                redis_client = redis.from_url(settings.REDIS_URL)
                limiter = _Limiter(
                    key_func=get_remote_address,
                    storage_uri=settings.REDIS_URL,
                    strategy="fixed-window",
                )
                logger.info("Rate limiter initialized with Redis storage")
            except Exception:
                logger.warning(
                    "Failed to connect to Redis for rate limiting: {e}. Using memory storage."
                )
                limiter = _Limiter(key_func=get_remote_address)
        else:
            limiter = _Limiter(key_func=get_remote_address)
            logger.info("Rate limiter initialized with memory storage")
    except Exception:
        logger.error("Failed to initialize rate limiter: {e}")
        limiter = _Limiter(key_func=get_remote_address)

except ImportError:
    SLOWAPI_AVAILABLE = False

    # 空实现
    class _DummyLimiter:
        """slowapi 未安装时的空实现"""

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass

        def limit(self, *args: Any, **kwargs: Any) -> Callable:
            def decorator(f: Callable) -> Callable:
                return f

            return decorator

    def _dummy_get_remote_address(request: Any) -> str:
        return "127.0.0.1"

    get_remote_address = _dummy_get_remote_address
    limiter = _DummyLimiter()

    logger.warning(
        "slowapi not installed, rate limiting disabled. Install with: pip install slowapi"
    )


def setup_rate_limiter(app: FastAPI) -> None:
    """
    配置限流器到 FastAPI 应用

    Usage:
        from app.core.rate_limiter import setup_rate_limiter
        setup_rate_limiter(app)
    """
    if SLOWAPI_AVAILABLE and limiter is not None:
        app.state.limiter = limiter
        if _rate_limit_exceeded_handler is not None:
            app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
        logger.info("Rate limiter configured")
    else:
        logger.warning("Rate limiter not configured (slowapi not installed)")


# 预定义的限流策略
class RateLimitConfig:
    """限流配置常量"""

    # 登录接口：5次/分钟
    LOGIN = "5/minute"

    # 注册接口：3次/分钟
    REGISTER = "3/minute"

    # 发送验证码：1次/分钟
    SEND_CODE = "1/minute"

    # 普通 API：100次/分钟
    DEFAULT = "100/minute"

    # 文件上传：10次/分钟
    UPLOAD = "10/minute"

    # 导出数据：5次/分钟
    EXPORT = "5/minute"


def get_limiter() -> Any:
    """获取限流器实例（用于依赖注入）"""
    return limiter


def rate_limit(requests: str, key_func: Callable | None = None) -> Callable:
    """
    限流装饰器快捷方式

    如果 slowapi 未安装，装饰器将不起作用（直接返回原函数）

    Usage:
        @router.post("/login")
        @rate_limit(RateLimitConfig.LOGIN)
        async def login(...):
            ...
    """

    def decorator(func: Callable) -> Callable:
        if SLOWAPI_AVAILABLE and limiter is not None:
            return limiter.limit(requests, key_func=key_func)(func)
        else:
            # slowapi 未安装，返回原函数
            return func

    return decorator
