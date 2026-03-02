"""
统一验证工具
提供可复用的验证函数和 Pydantic 验证器
"""

import re

from fastapi_babel import _
from pydantic import field_validator


class ValidationPatterns:
    """常用验证正则表达式"""

    # 用户名：字母开头，可包含字母、数字、下划线，3-32字符
    USERNAME = r"^[A-Za-z][A-Za-z0-9_]{2,31}$"

    # 密码：至少6位，包含大小写字母和数字
    PASSWORD_STRONG = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{6,}$"

    # 密码：至少6位
    PASSWORD_SIMPLE = r"^.{6,}$"

    # 邮箱
    EMAIL = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

    # 手机号：中国大陆
    MOBILE_CN = r"^1[3-9]\d{9}$"

    # 手机号：国际格式
    MOBILE_INTL = r"^\+?[1-9]\d{1,14}$"

    # 昵称：字母、数字、中文、下划线、横线、空格，2-50字符
    NICKNAME = r"^[\w\s\-\u4e00-\u9fa5]{2,50}$"

    # URL
    URL = r"^https?://[^\s/$.?#].[^\s]*$"

    # IP 地址
    IP = r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"


class Validators:
    """验证函数集合"""

    @staticmethod
    def username(value: str) -> str:
        """验证用户名"""
        if not re.match(ValidationPatterns.USERNAME, value):
            raise ValueError(
                _(
                    "Username must start with a letter, can contain letters, numbers, "
                    "and underscores, and be 3-32 characters long."
                )
            )
        return value

    @staticmethod
    def password(value: str, strong: bool = True) -> str:
        """验证密码"""
        if strong:
            if len(value) < 6:
                raise ValueError(_("Password must be at least 6 characters long."))
            if not re.search(r"[A-Z]", value):
                raise ValueError(_("Password must contain at least one uppercase letter."))
            if not re.search(r"[a-z]", value):
                raise ValueError(_("Password must contain at least one lowercase letter."))
            if not re.search(r"\d", value):
                raise ValueError(_("Password must contain at least one digit."))
        else:
            if len(value) < 6:
                raise ValueError(_("Password must be at least 6 characters long."))
        return value

    @staticmethod
    def email(value: str) -> str:
        """验证邮箱"""
        if not re.match(ValidationPatterns.EMAIL, value):
            raise ValueError(_("A valid email address is required."))
        if len(value) > 100:
            raise ValueError(_("Email too long (max 100 characters)."))
        return value

    @staticmethod
    def mobile(value: str, country: str = "CN") -> str:
        """验证手机号"""
        if country == "CN":
            if not re.match(ValidationPatterns.MOBILE_CN, value):
                raise ValueError(_("Invalid mobile number format."))
        else:
            if not re.match(ValidationPatterns.MOBILE_INTL, value):
                raise ValueError(_("Invalid mobile number format."))
        return value

    @staticmethod
    def nickname(value: str) -> str:
        """验证昵称"""
        if not re.match(ValidationPatterns.NICKNAME, value):
            raise ValueError(
                _(
                    "Nickname can contain letters, numbers, Chinese characters, "
                    "underscores, hyphens, and spaces, 2-50 characters."
                )
            )
        return value


# Pydantic field_validator 快捷方式
def validate_username_field(field_name: str = "username"):
    """创建用户名字段验证器"""

    @field_validator(field_name)
    @classmethod
    def validator(cls, v):
        return Validators.username(v)

    return validator


def validate_password_field(field_name: str = "password", strong: bool = True):
    """创建密码字段验证器"""

    @field_validator(field_name)
    @classmethod
    def validator(cls, v):
        # 允许 None 或空字符串（用于更新场景）
        if v is None or v == "":
            return v
        return Validators.password(v, strong=strong)

    return validator


def validate_email_field(field_name: str = "email"):
    """创建邮箱字段验证器"""

    @field_validator(field_name)
    @classmethod
    def validator(cls, v):
        if v is None or v == "":
            return v
        return Validators.email(v)

    return validator


def validate_mobile_field(field_name: str = "mobile", country: str = "CN"):
    """创建手机号字段验证器"""

    @field_validator(field_name)
    @classmethod
    def validator(cls, v):
        if v is None or v == "":
            return v
        return Validators.mobile(v, country=country)

    return validator


def validate_nickname_field(field_name: str = "nickname"):
    """创建昵称字段验证器"""

    @field_validator(field_name)
    @classmethod
    def validator(cls, v):
        if v is None or v == "":
            return v
        return Validators.nickname(v)

    return validator


# 组合验证器（用于更新时密码可选的场景）
class OptionalPasswordValidator:
    """
    可选密码验证器

    Usage:
        class UserUpdate(BaseModel):
            password: Optional[str] = None

            _validate_password = validate_optional_password()
    """

    @staticmethod
    def create(strong: bool = True):
        @field_validator("password")
        @classmethod
        def validator(cls, v):
            if v is None or v == "":
                return v
            return Validators.password(v, strong=strong)

        return validator


# 使用示例
"""
from pydantic import BaseModel
from app.core.validators import (
    validate_username_field,
    validate_password_field,
    validate_email_field,
    validate_mobile_field
)

class UserCreate(BaseModel):
    username: str
    password: str
    email: str
    mobile: str
    
    # 添加验证器
    _validate_username = validate_username_field()
    _validate_password = validate_password_field()
    _validate_email = validate_email_field()
    _validate_mobile = validate_mobile_field()

class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    email: Optional[str] = None
    mobile: Optional[str] = None
    
    # 更新时密码可选
    _validate_username = validate_username_field()
    _validate_password = validate_password_field()  # 自动处理 None/空字符串
    _validate_email = validate_email_field()
    _validate_mobile = validate_mobile_field()
"""
