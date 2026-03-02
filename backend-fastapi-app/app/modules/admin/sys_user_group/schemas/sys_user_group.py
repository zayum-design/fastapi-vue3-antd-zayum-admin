from datetime import UTC, datetime
from typing import Literal

from fastapi_babel import _
from pydantic import BaseModel, Field, field_validator


class SysUserGroupBase(BaseModel):
    id: int | None = Field(None)
    pid: int = Field(...)
    name: str = Field(..., max_length=100)
    rules: dict = Field(...)
    access: dict = Field(...)
    status: Literal["normal", "hidden"] = Field(..., max_length=6)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("status")
    def validate_status(cls, v):
        if v not in ["normal", "hidden"]:
            raise ValueError(_("STATUS should be either normal or hidden"))
        return v

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class SysUserGroupCreate(SysUserGroupBase):
    pass


class SysUserGroupUpdate(BaseModel):
    pid: int | None = None
    name: str | None = Field(None, max_length=100)
    rules: dict | None = None
    access: dict | None = None
    status: Literal["normal", "hidden"] | None = Field(None, max_length=6)

    class Config:
        from_attributes = True


class SysUserGroupInDBBase(SysUserGroupBase):
    pass


class SysUserGroup(SysUserGroupInDBBase):
    pass
