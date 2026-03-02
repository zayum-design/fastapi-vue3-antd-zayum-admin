"""
类型定义模块
提供项目中使用的类型别名、协议和通用类型
"""

from .common import (
    AdminID,
    Email,
    IPAddress,
    JsonDict,
    JsonList,
    ModelID,
    PhoneNumber,
    Status,
    Timestamp,
    Token,
    UserID,
)
from .protocols import CRUDProtocol, ModelProtocol, RepositoryProtocol

__all__ = [
    # 基础类型
    "JsonDict",
    "JsonList",
    "AdminID",
    "UserID",
    "ModelID",
    "Timestamp",
    "IPAddress",
    "Email",
    "PhoneNumber",
    "Token",
    "Status",
    # 协议
    "CRUDProtocol",
    "ModelProtocol",
    "RepositoryProtocol",
]
