"""
代码生成器工具函数
"""

from typing import Optional
import datetime
import decimal
from sqlalchemy import Enum as SqlEnum


def map_sql_type_to_ts(col_type) -> str:
    """将SQL类型映射到TypeScript类型"""
    if isinstance(col_type, SqlEnum):
        return "string"
    if hasattr(col_type, "python_type"):
        py_type = col_type.python_type
        if py_type == int:
            return "number"
        elif py_type == float:
            return "number"
        elif py_type == bool:
            return "boolean"
        elif py_type == str:
            return "string"
        elif py_type == bytes:
            return "string"
        elif py_type in [datetime.datetime, datetime.date]:
            return "string"
    return "any"


def default_value(col_type, server_default: Optional[str] = None) -> str:
    """根据字段类型获取默认值"""
    if isinstance(col_type, SqlEnum):
        return f"'{col_type.enums[0]}'"
    if hasattr(col_type, "python_type"):
        py_type = col_type.python_type
        if py_type == int:
            return "0"
        elif py_type == float:
            return "0.0"
        elif py_type == bool:
            return "false"
        elif py_type == str:
            return "''"
        elif py_type == bytes:
            return "''"
        elif py_type in [datetime.datetime]:
            return "dayjs().tz(TIME_ZONE).format('YYYY-MM-DD HH:mm:ss')"
        elif py_type in [datetime.date]:
            return "dayjs().tz(TIME_ZONE).format('YYYY-MM-DD')"
        elif py_type in [decimal.Decimal]:
            return "0.0"
    return "null"
