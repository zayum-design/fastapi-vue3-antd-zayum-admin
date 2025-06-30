from datetime import datetime, date, timezone
from decimal import Decimal
from typing import Optional, Literal
from pydantic import BaseModel, Field, EmailStr, field_validator
from fastapi_babel import _
import re


class SysAdminBase(BaseModel):
    id: Optional[int] = Field(None)
    group_id: int = Field(...)
    username: str = Field(..., max_length=20)
    nickname: str = Field(..., max_length=50)
    password: str = Field(..., max_length=128)
    avatar: Optional[str] = None
    email: EmailStr = Field(..., max_length=100)
    mobile: str = Field(..., max_length=11)
    login_failure: int = Field(...)
    login_at: Optional[datetime] = None
    login_ip: Optional[str] = None
    token: Optional[str] = None
    status: Literal['normal', 'hidden'] = Field(..., max_length=6)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[A-Za-z][A-Za-z0-9_]{2,31}$', v):
            raise ValueError(_('Username must start with a letter, can contain letters, numbers, and underscores, and be 3-32 characters long.'))
        return v

    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError(_('Password must be at least 6 characters long.'))
        if not re.search(r'[A-Z]', v):
            raise ValueError(_('Password must contain at least one uppercase letter.'))
        if not re.search(r'[a-z]', v):
            raise ValueError(_('Password must contain at least one lowercase letter.'))
        if not re.search(r'\d', v):
            raise ValueError(_('Password must contain at least one digit.'))
        return v

    @field_validator('email')
    def validate_email(cls, v):
        email_regex = r'^[A-Za-z0-9\._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
        if not re.match(email_regex, v) or len(v) > 100:
            raise ValueError(_('A valid email address is required.'))
        return v

    @field_validator('mobile')
    def validate_mobile(cls, v):
        if not v.isdigit():
            raise ValueError(_('Mobile number must contain only digits.'))
        if not (10 <= len(v) <= 16):
            raise ValueError(_('Mobile number must be between 10 and 16 digits long.'))
        return v

    @field_validator('status')
    def validate_status(cls, v):
        if v not in ['normal', 'hidden']:
            raise ValueError(_('STATUS should be either normal or hidden'))
        return v

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class SysAdminCreate(SysAdminBase):
    pass

class SysAdminUpdate(BaseModel):
    group_id: Optional[int] = None
    username: Optional[str] = Field(None, max_length=20)
    nickname: Optional[str] = Field(None, max_length=50)
    password: Optional[str] = Field(None, max_length=128)
    avatar: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = Field(None, max_length=100)
    mobile: Optional[str] = Field(None, max_length=11)
    login_failure: Optional[int] = None
    login_at: Optional[datetime] = None
    login_ip: Optional[str] = Field(None, max_length=50)
    token: Optional[str] = Field(None, max_length=512)
    status: Optional[Literal['normal', 'hidden']] = Field(None, max_length=6)

    class Config:
        orm_mode = True

class SysAdminInDBBase(SysAdminBase):
    pass

class SysAdmin(SysAdminInDBBase):
    pass
