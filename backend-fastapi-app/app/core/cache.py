# app/core/cache.py
import redis.asyncio as redis
from app.core.config import settings  # 确保正确导入 settings
from app.utils.log_utils import logger

async def get_redis():
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
