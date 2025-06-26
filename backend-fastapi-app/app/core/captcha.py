# app/core/captcha.py
import random
import string
from io import BytesIO
from captcha.image import ImageCaptcha
from fastapi import HTTPException, status
from app.core.cache import get_redis

# 如果没有安装 Redis，使用内存缓存
try:
    import redis
    USE_REDIS = True
except ImportError:
    USE_REDIS = False

# 内存缓存字典
memory_cache = {}

async def generate_captcha():
    # 生成4位随机验证码
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    
    # 使用 captcha 库生成验证码图片
    image = ImageCaptcha(width=120, height=40)  # 设置图片大小为 120x90
    captcha_image = image.generate(code)
    
    # 将图片保存到 BytesIO
    buffer = BytesIO(captcha_image.getvalue())
    buffer.seek(0)
    
    # 生成唯一的 captcha_id
    captcha_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    
    # 缓存验证码
    if USE_REDIS:
        redis = await get_redis()
        await redis.set(f"captcha:{captcha_id}", code, ex=300)  # 5分钟有效
    else:
        memory_cache[captcha_id] = code
    
    return captcha_id, buffer.read()

async def verify_captcha(captcha_type: str, captcha: bool, captcha_id: str, captcha_code: str) -> bool:
    # 如果 captcha_type 不是 "code"，直接返回 True，不需要验证
    if captcha_type != "code":
        return captcha
    
    # 获取缓存的验证码
    if USE_REDIS:
        redis = await get_redis()
        stored_code = await redis.get(f"captcha:{captcha_id}")
    else:
        stored_code = memory_cache.get(captcha_id)
    
    # 验证码不存在或已过期
    if not stored_code:
        return False
    
    # 验证码匹配
    if stored_code.lower() != captcha_code.lower():
        return False
    
    # 验证成功后删除验证码
    if USE_REDIS:
        await redis.delete(f"captcha:{captcha_id}")
    else:
        memory_cache.pop(captcha_id, None)
    
    return True
