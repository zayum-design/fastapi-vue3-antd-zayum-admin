import re
from datetime import UTC, datetime
from typing import Literal

from fastapi_babel import _
from pydantic import BaseModel, EmailStr, Field, field_validator


class SysAdminBase(BaseModel):
    id: int | None = Field(None)
    group_id: int = Field(...)
    username: str = Field(..., max_length=20)
    nickname: str = Field(..., max_length=50)
    password: str = Field(..., max_length=128)
    avatar: str | None = None
    email: EmailStr = Field(..., max_length=100)
    mobile: str = Field(..., max_length=11)
    login_failure: int = Field(...)
    login_at: datetime | None = None
    login_ip: str | None = None
    token: str | None = None
    status: Literal["normal", "hidden"] = Field(..., max_length=6)
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

    @field_validator("status")
    def validate_status(cls, v):
        if v not in ["normal", "hidden"]:
            raise ValueError(_("STATUS should be either normal or hidden"))
        return v

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class SysAdminCreate(SysAdminBase):
    pass


class SysAdminUpdate(BaseModel):
    group_id: int | None = None
    username: str | None = Field(None, max_length=20)
    nickname: str | None = Field(None, max_length=50)
    password: str | None = Field(None, max_length=128)
    avatar: str | None = Field(None, max_length=255)
    email: EmailStr | None = Field(None, max_length=100)
    mobile: str | None = Field(None, max_length=11)
    login_failure: int | None = None
    login_at: datetime | None = None
    login_ip: str | None = Field(None, max_length=50)
    token: str | None = Field(None, max_length=512)
    status: Literal["normal", "hidden"] | None = Field(None, max_length=6)

    @field_validator("password")
    def validate_password(cls, v):
        # 在更新模式下，密码为空时直接通过验证（表示不修改密码）
        if v is None or v == "":
            return v
        # 只有在密码不为空时才进行密码强度验证
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


class SysAdminInDBBase(SysAdminBase):
    pass


class SysAdmin(SysAdminInDBBase):
    pass
