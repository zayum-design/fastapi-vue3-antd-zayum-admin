from datetime import datetime, date, timezone
from decimal import Decimal
from typing import Optional, Literal
from pydantic import BaseModel, Field, EmailStr, field_validator
from fastapi_babel import _
import re


class SysNotificationBase(BaseModel):
    id: int = Field(...)
    receiver_id: int = Field(...)
    receiver_type: str = Field(Field(...), max_length=20)
    sender_id: Optional[int] = None
    sender_name: Optional[str] = None
    title: str = Field(Field(...), max_length=100)
    message: str = Field(Field(...))
    type: Literal['system', 'message', 'comment', 'reminder', 'approval', 'security', 'update', 'task'] = Field(Field(...), max_length=8)
    status: Literal['normal', 'hidden'] = Field(Field(...), max_length=6)
    avatar: Optional[str] = None
    related_id: Optional[int] = None
    related_type: Optional[str] = None
    related_url: Optional[str] = None
    priority: int = Field(...)
    expires_at: Optional[datetime] = None
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


class SysNotificationCreate(SysNotificationBase):
    pass

class SysNotificationUpdate(BaseModel):
    receiver_id: Optional[int] = None
    receiver_type: Optional[str] = Field(None, max_length=20)
    sender_id: Optional[int] = None
    sender_name: Optional[str] = Field(None, max_length=50)
    title: Optional[str] = Field(None, max_length=100)
    message: Optional[str] = Field(None)
    type: Optional[Literal['system', 'message', 'comment', 'reminder', 'approval', 'security', 'update', 'task']] = Field(None, max_length=8)
    status: Optional[Literal['normal', 'hidden']] = Field(None, max_length=6)
    avatar: Optional[str] = Field(None, max_length=255)
    related_id: Optional[int] = None
    related_type: Optional[str] = Field(None, max_length=50)
    related_url: Optional[str] = Field(None, max_length=500)
    priority: Optional[int] = None
    expires_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class SysNotificationInDBBase(SysNotificationBase):
    pass

class SysNotification(SysNotificationInDBBase):
    pass

