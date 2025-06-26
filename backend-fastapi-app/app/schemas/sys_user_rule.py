from datetime import datetime, date, timezone
from decimal import Decimal
from typing import Optional, Literal
from pydantic import BaseModel, Field, EmailStr, field_validator
from fastapi_babel import _
import re


class SysUserRuleBase(BaseModel):
    id: int = Field(...)
    type: Literal['menu', 'action'] = Field(Field(...), max_length=6)
    pid: int = Field(...)
    plugin: int = Field(...)
    name: str = Field(Field(...), max_length=150)
    url_path: str = Field(Field(...), max_length=50)
    title: str = Field(Field(...), max_length=50)
    description: Optional[str] = None
    icon: Optional[str] = None
    menutype: Optional[Literal['addtabs', 'blank', 'dialog', 'ajax']] = None
    extend: Optional[str] = None
    model_name: str = Field(Field(...), max_length=50)
    weigh: int = Field(...)
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


class SysUserRuleCreate(SysUserRuleBase):
    id: Optional[int] = None
    pass

class SysUserRuleUpdate(BaseModel):
    type: Optional[Literal['menu', 'action']] = Field(None, max_length=6)
    pid: Optional[int] = None
    plugin: Optional[int] = None
    name: Optional[str] = Field(None, max_length=150)
    url_path: Optional[str] = Field(None, max_length=50)
    title: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    icon: Optional[str] = Field(None, max_length=50)
    menutype: Optional[Literal['addtabs', 'blank', 'dialog', 'ajax']] = Field(None, max_length=7)
    extend: Optional[str] = Field(None, max_length=255)
    model_name: Optional[str] = Field(None, max_length=50)
    weigh: Optional[int] = None
    status: Optional[Literal['normal', 'hidden']] = Field(None, max_length=6)

    class Config:
        orm_mode = True

class SysUserRuleInDBBase(SysUserRuleBase):
    id: int
    type: Optional[Literal['menu', 'action']] = None
    pid: Optional[int] = None
    plugin: Optional[int] = None
    name: Optional[str] = None
    url_path: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    menutype: Optional[Literal['addtabs', 'blank', 'dialog', 'ajax']] = None
    extend: Optional[str] = None
    model_name: Optional[str] = None
    weigh: Optional[int] = None
    status: Optional[Literal['normal', 'hidden']] = None

    class Config:
        orm_mode = True

class SysUserRule(SysUserRuleInDBBase):
    pass

