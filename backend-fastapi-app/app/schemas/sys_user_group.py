from datetime import datetime, date, timezone
from decimal import Decimal
from typing import Optional, Literal
from pydantic import BaseModel, Field, EmailStr, field_validator
from fastapi_babel import _
import re


class SysUserGroupBase(BaseModel):
    id: int = Field(...)
    pid: int = Field(...)
    name: str = Field(Field(...), max_length=100)
    rules: dict = Field(...)
    access: dict = Field(...)
    status: Literal['normal', 'hidden'] = Field(Field(...), max_length=6)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator('status')
    def validate_status(cls, v):
        if v not in ['normal', 'hidden']:
            raise ValueError(_('STATUS should be either normal or hidden'))
        return v

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class SysUserGroupCreate(SysUserGroupBase):
    pass

class SysUserGroupUpdate(BaseModel):
    pid: Optional[int] = None
    name: Optional[str] = Field(None, max_length=100)
    rules: Optional[dict] = None
    access: Optional[dict] = None
    status: Optional[Literal['normal', 'hidden']] = Field(None, max_length=6)

    class Config:
        orm_mode = True

class SysUserGroupInDBBase(SysUserGroupBase):
    pass

class SysUserGroup(SysUserGroupInDBBase):
    pass

