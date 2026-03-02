"""
通用类型别名
"""

from datetime import datetime
from typing import Any, NewType, Union

# JSON 类型
JsonDict = dict[str, Any]
"""JSON 对象类型"""

JsonList = list[Any]
"""JSON 数组类型"""

JsonValue = Union[str, int, float, bool, None, JsonDict, JsonList]
"""JSON 值类型"""

# ID 类型
AdminID = NewType("AdminID", int)
"""管理员 ID 类型"""

UserID = NewType("UserID", int)
"""用户 ID 类型"""

ModelID = NewType("ModelID", int)
"""通用模型 ID 类型"""

# 时间类型
Timestamp = Union[datetime, str, int, float]
"""时间戳类型（支持 datetime、ISO 格式字符串、Unix 时间戳）"""

# 字符串类型别名
IPAddress = NewType("IPAddress", str)
"""IP 地址类型"""

Email = NewType("Email", str)
"""邮箱地址类型"""

PhoneNumber = NewType("PhoneNumber", str)
"""手机号码类型"""

Token = NewType("Token", str)
"""令牌类型"""

Status = NewType("Status", str)
"""状态类型"""

# 业务类型
PageNumber = NewType("PageNumber", int)
"""页码类型"""

PageSize = NewType("PageSize", int)
"""每页数量类型"""

SearchQuery = NewType("SearchQuery", str)
"""搜索查询类型"""

OrderBy = NewType("OrderBy", str)
"""排序字段类型"""

# 响应类型
ResponseCode = NewType("ResponseCode", int)
"""响应码类型"""

ResponseMessage = NewType("ResponseMessage", str)
"""响应消息类型"""

# 文件类型
FilePath = NewType("FilePath", str)
"""文件路径类型"""

FileName = NewType("FileName", str)
"""文件名类型"""

MIMEType = NewType("MIMEType", str)
"""MIME 类型"""

# 配置类型
ConfigKey = NewType("ConfigKey", str)
"""配置键类型"""

ConfigValue = Union[str, int, float, bool, None]
"""配置值类型"""

# 权限类型
PermissionCode = NewType("PermissionCode", str)
"""权限代码类型"""

RoleCode = NewType("RoleCode", str)
"""角色代码类型"""
