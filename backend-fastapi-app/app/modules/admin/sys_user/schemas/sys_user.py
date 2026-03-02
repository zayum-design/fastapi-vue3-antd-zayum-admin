import re
from datetime import UTC, datetime
from decimal import Decimal
from typing import Literal

from fastapi_babel import _
from pydantic import BaseModel, EmailStr, Field, field_validator


class SysUserBase(BaseModel):
    id: int | None = Field(None)
    user_group_id: int = Field(...)
    username: str = Field(..., max_length=32)
    nickname: str = Field(..., max_length=50)
    password: str = Field(..., max_length=120)
    email: EmailStr = Field(..., max_length=100)
    mobile: str = Field(..., max_length=16)
    avatar: str | None = None
    level: int = Field(...)
    gender: Literal["female", "male"] = Field(..., max_length=6)
    birthday: str | None = None
    bio: str | None = None
    balance: Decimal | None = None
    score: int = Field(...)
    successions: int | None = None
    max_successions: int | None = None
    prev_time: datetime | None = None
    login_time: datetime | None = None
    login_ip: str | None = None
    login_failure: int | None = None
    join_ip: str | None = None
    verification: str | None = None
    token: str | None = None
    status: Literal["normal", "hidden"] | None = None
    platform: Literal["ios", "mac", "android", "web", "pc", "other"] = Field(
        default="other", max_length=10
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("username")
    def validate_username(cls, v):
        if not re.match(r"^[A-Za-z][A-Za-z0-9_]{2,31}$", v):
            raise ValueError(
                _(
                    "Username must start with a letter, can contain letters, numbers, and underscores, and be 3-32 characters long."
                )
            )
        return v

    @field_validator("password")
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError(_("Password must be at least 6 characters long."))
        if not re.search(r"[A-Z]", v):
            raise ValueError(_("Password must contain at least one uppercase letter."))
        if not re.search(r"[a-z]", v):
            raise ValueError(_("Password must contain at least one lowercase letter."))
        if not re.search(r"\d", v):
            raise ValueError(_("Password must contain at least one digit."))
        return v

    @field_validator("email")
    def validate_email(cls, v):
        email_regex = r"^[A-Za-z0-9\._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
        if not re.match(email_regex, v) or len(v) > 100:
            raise ValueError(_("A valid email address is required."))
        return v

    @field_validator("mobile")
    def validate_mobile(cls, v):
        if not v.isdigit():
            raise ValueError(_("Mobile number must contain only digits."))
        if not (10 <= len(v) <= 16):
            raise ValueError(_("Mobile number must be between 10 and 16 digits long."))
        return v

    @field_validator("gender")
    def validate_gender(cls, v):
        if v not in ["female", "male"]:
            raise ValueError(_("GENDER should be either female or male"))
        return v

    @field_validator("status")
    def validate_status(cls, v):
        if v not in ["normal", "hidden"]:
            raise ValueError(_("STATUS should be either normal or hidden"))
        return v

    @field_validator("platform")
    def validate_platform(cls, v):
        if v not in ["ios", "mac", "android", "web", "pc", "other"]:
            raise ValueError(_("PLATFORM should be one of: ios, mac, android, web, pc, other"))
        return v

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        json_encoders = {Decimal: lambda v: str(v)}


class SysUserCreate(SysUserBase):
    pass


class SysUserUpdate(BaseModel):
    user_group_id: int | None = None
    username: str | None = Field(None, max_length=32)
    nickname: str | None = Field(None, max_length=50)
    password: str | None = Field(None, max_length=120)
    email: EmailStr | None = Field(None, max_length=100)
    mobile: str | None = Field(None, max_length=16)
    avatar: str | None = Field(None, max_length=255)
    level: int | None = None
    gender: Literal["female", "male"] | None = Field(None, max_length=6)
    birthday: str | None = None
    bio: str | None = Field(None, max_length=100)
    balance: Decimal | None = None
    score: int | None = None
    successions: int | None = None
    max_successions: int | None = None
    prev_time: datetime | None = None
    login_time: datetime | None = None
    login_ip: str | None = Field(None, max_length=50)
    login_failure: int | None = None
    join_ip: str | None = Field(None, max_length=50)
    verification: str | None = Field(None, max_length=255)
    token: str | None = Field(None, max_length=250)
    status: Literal["normal", "hidden"] | None = Field(None, max_length=6)
    platform: Literal["ios", "mac", "android", "web", "pc", "other"] | None = Field(
        None, max_length=10
    )

    @field_validator("password")
    def validate_password(cls, v):
        # 在更新时，密码可以为空（表示不修改密码）
        if v is None or v == "":
            return v
        if len(v) < 6:
            raise ValueError(_("Password must be at least 6 characters long."))
        if not re.search(r"[A-Z]", v):
            raise ValueError(_("Password must contain at least one uppercase letter."))
        if not re.search(r"[a-z]", v):
            raise ValueError(_("Password must contain at least one lowercase letter."))
        if not re.search(r"\d", v):
            raise ValueError(_("Password must contain at least one digit."))
        return v

    class Config:
        from_attributes = True


class SysUserInDBBase(SysUserBase):
    pass


class SysUser(SysUserInDBBase):
    pass
