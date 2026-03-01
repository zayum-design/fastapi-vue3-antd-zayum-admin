"""
代码生成器插件
提供数据库表到代码的自动生成功能
"""

from .plugin import register, unregister

__all__ = ["register", "unregister"]
