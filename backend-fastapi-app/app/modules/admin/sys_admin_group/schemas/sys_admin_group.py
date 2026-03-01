from datetime import datetime, date, timezone
from decimal import Decimal
from typing import Optional, Literal
from pydantic import BaseModel, Field, EmailStr, field_validator
from fastapi_babel import _
import re


class SysAdminGroupBase(BaseModel):
    id: Optional[int] = Field(None)
    pid: int = Field(...)
    name: str = Field(..., max_length=100)
    rules: list = Field(...)
    access: list = Field(...)
    status: Literal['normal', 'hidden'] = Field(..., max_length=6)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator('status')
    def validate_status(cls, v):
        if v not in ['normal', 'hidden']:
            raise ValueError(_('STATUS should be either normal or hidden'))
        return v

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class SysAdminGroupCreate(SysAdminGroupBase):
    pass

class SysAdminGroupUpdate(BaseModel):
    pid: Optional[int] = None
    name: Optional[str] = Field(None, max_length=100)
    rules: Optional[list] = None
    access: Optional[list] = None
    status: Optional[Literal['normal', 'hidden']] = Field(None, max_length=6)

    class Config:
        from_attributes = True

class SysAdminGroupInDBBase(SysAdminGroupBase):
    pass

class SysAdminGroup(SysAdminGroupInDBBase):
    pass
