from datetime import datetime, date, timezone
from decimal import Decimal
from typing import Optional, Literal
from pydantic import BaseModel, Field, EmailStr, field_validator
from fastapi_babel import _
import re


class SysAdminLogBase(BaseModel):
    id: int = Field(...)
    admin_id: int = Field(...)
    username: str = Field(Field(...), max_length=30)
    url: str = Field(Field(...), max_length=1500)
    title: Optional[str] = None
    content: str = Field(Field(...))
    ip: str = Field(Field(...), max_length=50)
    useragent: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[A-Za-z][A-Za-z0-9_]{2,31}$', v):
            raise ValueError(_('Username must start with a letter, can contain letters, numbers, and underscores, and be 3-32 characters long.'))
        return v

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class SysAdminLogCreate(SysAdminLogBase):
    id: Optional[int] = None
    pass

class SysAdminLogUpdate(BaseModel):
    admin_id: Optional[int] = None
    username: Optional[str] = Field(None, max_length=30)
    url: Optional[str] = Field(None, max_length=1500)
    title: Optional[str] = Field(None, max_length=100)
    content: Optional[str] = Field(None)
    ip: Optional[str] = Field(None, max_length=50)
    useragent: Optional[str] = Field(None)

    class Config:
        orm_mode = True

class SysAdminLogInDBBase(SysAdminLogBase):
    id: int
    admin_id: Optional[int] = None
    username: Optional[str] = None
    url: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    ip: Optional[str] = None
    useragent: Optional[str] = None

    class Config:
        orm_mode = True

class SysAdminLog(SysAdminLogInDBBase):
    pass

