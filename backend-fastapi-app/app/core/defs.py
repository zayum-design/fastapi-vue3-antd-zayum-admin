import json
import os
from datetime import datetime
from pathlib import Path
import re
import importlib
import string
import random
from collections import defaultdict
from urllib.parse import urlparse, urljoin
import inspect
from sqlalchemy import inspect as sqlalchemyInspect
from app.core import db
from app.core.utils.defs import now

from app.core.utils.logger import logger


def get_timestamp():
    """
    获取当前时间戳
    :return: 当前时间戳
    """
    from datetime import datetime

    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def is_safe_url(request, target):
    """
    判断目标 URL 是否为安全的 URL（防止 Open Redirect 攻击）。
    :param target: 目标 URL 字符串
    :return: 如果目标 URL 与当前主机相同且使用 http 或 https 协议，则返回 True；否则返回 False
    """
    ref_url = urlparse(request.host_url)  # 解析当前请求的主机 URL
    test_url = urlparse(
        urljoin(request.host_url, target)
    )  # 将目标 URL 与主机 URL 合并并解析

    # 判断协议是否为 http 或 https，且主机名相同
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc

 
def generate_random_string(length):
    """Generate a random string of a given length."""
    # 定义可能的字符集合
    characters = string.ascii_letters + string.digits

    # 使用random.choices函数从字符集合中随机选择指定数量的字符，然后用join合并为一个字符串
    random_string = "".join(random.choices(characters, k=length))

    return random_string
