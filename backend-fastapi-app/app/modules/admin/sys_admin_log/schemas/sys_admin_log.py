import re
from datetime import UTC, datetime

from fastapi_babel import _
from pydantic import BaseModel, Field, field_validator


class SysAdminLogBase(BaseModel):
    id: int | None = Field(None)
    admin_id: int = Field(...)
    username: str = Field(..., max_length=30)
    url: str = Field(..., max_length=1500)
    title: str | None = None
    content: str = Field(...)
    ip: str = Field(..., max_length=50)
    useragent: str | None = None
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

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class SysAdminLogCreate(SysAdminLogBase):
    pass


class SysAdminLogUpdate(BaseModel):
    admin_id: int | None = None
    username: str | None = Field(None, max_length=30)
    url: str | None = Field(None, max_length=1500)
    title: str | None = Field(None, max_length=100)
    content: str | None = Field(None)
    ip: str | None = Field(None, max_length=50)
    useragent: str | None = Field(None)

    class Config:
        from_attributes = True


class SysAdminLogInDBBase(SysAdminLogBase):
    pass


class SysAdminLog(SysAdminLogInDBBase):
    pass
