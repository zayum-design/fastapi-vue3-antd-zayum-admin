# app/core/cache.py
"""
通用缓存管理类
支持简单内存缓存和Redis缓存，通过环境变量配置
"""
import time
import json
import asyncio
from typing import Any, Optional, Dict
import redis.asyncio as redis
from app.core.config import settings
from app.utils.log_utils import logger


class SimpleCache:
    """
    简单内存缓存实现
    """
    def __init__(self):
        self._cache = {}
        self._expire_times = {}
    
    async def get(self, key: str) -> Optional[Any]:
        """从缓存获取数据"""
        try:
            if key in self._cache and key in self._expire_times:
                if time.time() < self._expire_times[key]:
                    logger.debug(f"SimpleCache: Cache hit for key {key}")
                    return self._cache[key]
                else:
                    # 缓存已过期，删除
                    del self._cache[key]
                    del self._expire_times[key]
                    logger.debug(f"SimpleCache: Cache expired for key {key}")
        except Exception as e:
            logger.warning(f"SimpleCache: Failed to get key {key}: {e}")
        return None
    
    async def set(self, key: str, value: Any, expire: int = 300):
        """设置缓存数据"""
        try:
            self._cache[key] = value
            self._expire_times[key] = time.time() + expire
            logger.debug(f"SimpleCache: Set cache for key {key}, expire in {expire}s")
        except Exception as e:
            logger.warning(f"SimpleCache: Failed to set key {key}: {e}")
    
    async def delete(self, key: str):
        """删除缓存数据"""
        try:
            if key in self._cache:
                del self._cache[key]
            if key in self._expire_times:
                del self._expire_times[key]
            logger.debug(f"SimpleCache: Deleted cache for key {key}")
        except Exception as e:
            logger.warning(f"SimpleCache: Failed to delete key {key}: {e}")
    
    async def delete_pattern(self, pattern: str):
        """按模式删除缓存数据"""
        try:
            keys_to_delete = [key for key in self._cache.keys() if pattern in key]
            for key in keys_to_delete:
                await self.delete(key)
            logger.info(f"SimpleCache: Deleted {len(keys_to_delete)} keys matching pattern: {pattern}")
        except Exception as e:
            logger.warning(f"SimpleCache: Failed to delete pattern {pattern}: {e}")


class RedisCache:
    """
    Redis缓存实现
    """
    def __init__(self):
        self.redis_client = None
        self._lock = asyncio.Lock()
    
    async def get_client(self) -> redis.Redis:
        """获取Redis客户端连接"""
        async with self._lock:
            if self.redis_client is None:
                try:
                    redis_url = str(settings.REDIS_URL)
                    self.redis_client = redis.from_url(redis_url, decode_responses=True)
                    await self.redis_client.ping()
                    logger.info("RedisCache: Connected to Redis successfully.")
                except Exception as e:
                    logger.error(f"RedisCache: Failed to connect to Redis: {e}")
                    raise
        return self.redis_client
    
    async def get(self, key: str) -> Optional[Any]:
        """从缓存获取数据"""
        try:
            client = await self.get_client()
            data = await client.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            logger.warning(f"RedisCache: Failed to get key {key}: {e}")
        return None
    
    async def set(self, key: str, value: Any, expire: int = 300):
        """设置缓存数据"""
        try:
            client = await self.get_client()
            await client.setex(key, expire, json.dumps(value))
        except Exception as e:
            logger.warning(f"RedisCache: Failed to set key {key}: {e}")
    
    async def delete(self, key: str):
        """删除缓存数据"""
        try:
            client = await self.get_client()
            await client.delete(key)
        except Exception as e:
            logger.warning(f"RedisCache: Failed to delete key {key}: {e}")
    
    async def delete_pattern(self, pattern: str):
        """按模式删除缓存数据"""
        try:
            client = await self.get_client()
            keys = await client.keys(pattern)
            if keys:
                await client.delete(*keys)
                logger.info(f"RedisCache: Deleted {len(keys)} keys matching pattern: {pattern}")
        except Exception as e:
            logger.warning(f"RedisCache: Failed to delete pattern {pattern}: {e}")


class CacheManager:
    """
    通用缓存管理器
    根据配置选择使用简单缓存或Redis缓存
    """
    def __init__(self):
        self._cache = None
        self._cache_type = settings.CACHE_TYPE.lower()
        
    async def _get_cache(self):
        """获取缓存实例"""
        if self._cache is None:
            if self._cache_type == "redis":
                self._cache = RedisCache()
                logger.info("CacheManager: Using Redis cache")
            else:
                self._cache = SimpleCache()
                logger.info("CacheManager: Using simple memory cache")
        return self._cache
    
    async def get(self, key: str) -> Optional[Any]:
        """从缓存获取数据"""
        cache = await self._get_cache()
        return await cache.get(key)
    
    async def set(self, key: str, value: Any, expire: int = 300):
        """设置缓存数据"""
        cache = await self._get_cache()
        await cache.set(key, value, expire)
    
    async def delete(self, key: str):
        """删除缓存数据"""
        cache = await self._get_cache()
        await cache.delete(key)
    
    async def delete_pattern(self, pattern: str):
        """按模式删除缓存数据"""
        cache = await self._get_cache()
        await cache.delete_pattern(pattern)


# 全局缓存管理器实例
cache_manager = CacheManager()


# 同步包装函数（用于同步API）
def get_cached_data_sync(key: str) -> Optional[Any]:
    """同步获取缓存数据"""
    try:
        return asyncio.run(cache_manager.get(key))
    except Exception as e:
        logger.warning(f"Failed to get cached data synchronously: {e}")
        return None


def set_cached_data_sync(key: str, value: Any, expire: int = 300):
    """同步设置缓存数据"""
    try:
        asyncio.run(cache_manager.set(key, value, expire))
    except Exception as e:
        logger.warning(f"Failed to set cached data synchronously: {e}")


def delete_cached_data_sync(key: str):
    """同步删除缓存数据"""
    try:
        asyncio.run(cache_manager.delete(key))
    except Exception as e:
        logger.warning(f"Failed to delete cached data synchronously: {e}")


def delete_cached_pattern_sync(pattern: str):
    """同步按模式删除缓存数据"""
    try:
        asyncio.run(cache_manager.delete_pattern(pattern))
    except Exception as e:
        logger.warning(f"Failed to delete cached pattern synchronously: {e}")


# 保留原有的 get_redis 函数用于向后兼容
async def get_redis():
    """获取Redis客户端连接（向后兼容）"""
    try:
        # 确保 settings.REDIS_URL 是字符串
        redis_url = str(settings.REDIS_URL)
        redis_client = redis.from_url(redis_url, decode_responses=True)
        await redis_client.ping()
        logger.info("Connected to Redis successfully.")
        return redis_client
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        raise
