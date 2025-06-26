# tests/test_env.py
import sys
import os

# 获取当前文件的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))

# 获取项目根目录（假设 `tests` 目录在根目录下）
project_root = os.path.dirname(current_dir)

# 将项目根目录添加到 sys.path
sys.path.append(project_root)

from app.core.config import settings

print(settings.dict())
