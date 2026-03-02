"""
缓存装饰器
提供函数级别的缓存支持
"""

import functools
import hashlib
import json
import pickle
from collections.abc import Callable
from typing import Any

from app.core.config import settings
from app.utils.log_utils import logger

# 缓存后端
cache_backend = None


def get_cache_backend():
    """获取缓存后端（延迟初始化）"""
    global cache_backend
    if cache_backend is None:
        if settings.CACHE_TYPE == "redis":
            try:
                import redis

                cache_backend = redis.from_url(settings.REDIS_URL, decode_responses=True)
                logger.info("Cache backend: Redis")
            except Exception:
                logger.warning("Failed to connect to Redis: {e}. Using memory cache.")
                cache_backend = {}
        else:
            cache_backend = {}
            logger.info("Cache backend: Memory")
    return cache_backend


class CacheManager:
    """缓存管理器"""

    def __init__(self):
        self._memory_cache = {}

    def _get_redis(self):
        backend = get_cache_backend()
        if isinstance(backend, dict):
            return None
        return backend

    def _is_redis(self) -> bool:
        return self._get_redis() is not None

    def get(self, key: str) -> Any | None:
        """获取缓存"""
        try:
            redis_client = self._get_redis()
            if redis_client:
                data = redis_client.get(key)
                if data:
                    return pickle.loads(data.encode("latin-1"))
            else:
                if key in self._memory_cache:
                    return self._memory_cache[key]
        except Exception:
            logger.error("Cache get error: {e}")
        return None

    def set(self, key: str, value: Any, timeout: int = 300):
        """设置缓存"""
        try:
            redis_client = self._get_redis()
            if redis_client:
                data = pickle.dumps(value).decode("latin-1")
                redis_client.setex(key, timeout, data)
            else:
                self._memory_cache[key] = value
        except Exception:
            logger.error("Cache set error: {e}")

    def delete(self, key: str):
        """删除缓存"""
        try:
            redis_client = self._get_redis()
            if redis_client:
                redis_client.delete(key)
            else:
                self._memory_cache.pop(key, None)
        except Exception:
            logger.error("Cache delete error: {e}")

    def delete_pattern(self, pattern: str):
        """按模式删除缓存"""
        try:
            redis_client = self._get_redis()
            if redis_client:
                keys = redis_client.keys(pattern)
                if keys:
                    redis_client.delete(*keys)
            else:
                keys_to_delete = [k for k in self._memory_cache.keys() if pattern in k]
                for k in keys_to_delete:
                    self._memory_cache.pop(k, None)
        except Exception:
            logger.error("Cache delete_pattern error: {e}")


# 全局缓存管理器实例
cache_manager = CacheManager()


def generate_cache_key(func: Callable, args: tuple, kwargs: dict) -> str:
    """生成缓存 key"""
    # 处理不可序列化的参数（如 Session、Request 等）
    from fastapi import Request
    from sqlalchemy.orm import Session

    filtered_args = []
    for arg in args:
        if isinstance(arg, (Session, Request)):
            continue
        filtered_args.append(arg)

    filtered_kwargs = {}
    for k, v in kwargs.items():
        if isinstance(v, (Session, Request)):
            continue
        filtered_kwargs[k] = v

    key_data = {"func": func.__qualname__, "args": filtered_args, "kwargs": filtered_kwargs}
    key_str = json.dumps(key_data, sort_keys=True, default=str)
    return (
        f"cache:{func.__module__}:{func.__qualname__}:{hashlib.md5(key_str.encode()).hexdigest()}"
    )


def cached(timeout: int = 300, key_prefix: str | None = None, unless: Callable | None = None):
    """
    缓存装饰器

    Args:
        timeout: 缓存过期时间（秒）
        key_prefix: 缓存 key 前缀
        unless: 条件函数，返回 True 时不缓存

    Usage:
        @cached(timeout=60, key_prefix="user_list")
        def get_users(db: Session):
            return db.query(User).all()
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 检查 unless 条件
            if unless and unless(*args, **kwargs):
                return func(*args, **kwargs)

            # 生成缓存 key
            if key_prefix:
                cache_key = f"cache:{key_prefix}:{generate_cache_key(func, args, kwargs)}"
            else:
                cache_key = generate_cache_key(func, args, kwargs)

            # 尝试从缓存获取
            cached_value = cache_manager.get(cache_key)
            if cached_value is not None:
                logger.debug("Cache hit: {cache_key}")
                return cached_value

            # 执行函数
            result = func(*args, **kwargs)

            # 存入缓存
            cache_manager.set(cache_key, result, timeout)
            logger.debug("Cache set: {cache_key}")

            return result

        # 添加清除缓存的方法
        wrapper.cache_key_prefix = key_prefix or func.__qualname__
        wrapper.cache_clear = lambda: cache_manager.delete_pattern(f"*{wrapper.cache_key_prefix}*")

        return wrapper

    return decorator


def cache_clear(key_prefix: str):
    """清除指定前缀的缓存"""
    cache_manager.delete_pattern(f"cache:{key_prefix}*")
    logger.info("Cache cleared: {key_prefix}")


# 装饰器：清除缓存
class clear_cache:
    """
    在函数执行后清除缓存

    Usage:
        @clear_cache("user_list")
        def update_user(db: Session, user_id: int):
            # 更新后自动清除 user_list 缓存
            ...
    """

    def __init__(self, *key_prefixes: str):
        self.key_prefixes = key_prefixes

    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            for prefix in self.key_prefixes:
                cache_clear(prefix)
            return result

        return wrapper
