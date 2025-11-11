from datetime import datetime, date, timezone
from decimal import Decimal
from typing import Optional, Literal
from pydantic import BaseModel, Field, EmailStr, field_validator
from fastapi_babel import _
import re


class SysUserRuleBase(BaseModel):
    id: int = Field(...)
    rule_type: Literal['menu', 'action'] = Field(Field(...), max_length=6)
    parent_id: int = Field(...)
    name: str = Field(Field(...), max_length=150)
    path: str = Field(Field(...), max_length=50)
    component: Optional[str] = None
    redirect: Optional[str] = None
    meta: Optional[dict] = None
    permission: Optional[dict] = None
    menu_display_type: Optional[Literal['ajax', 'addtabs', 'blank', 'dialog']] = None
    model_name: str = Field(Field(...), max_length=80)
    deleted_at: Optional[datetime] = None
    weigh: int = Field(...)
    status: Literal['normal', 'hidden'] = Field(Field(...), max_length=7)
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
    pass

class SysUserRuleUpdate(BaseModel):
    rule_type: Optional[Literal['menu', 'action']] = Field(None, max_length=6)
    parent_id: Optional[int] = None
    name: Optional[str] = Field(None, max_length=150)
    path: Optional[str] = Field(None, max_length=50)
    component: Optional[str] = Field(None, max_length=200)
    redirect: Optional[str] = Field(None, max_length=100)
    meta: Optional[dict] = None
    permission: Optional[dict] = None
    menu_display_type: Optional[Literal['ajax', 'addtabs', 'blank', 'dialog']] = Field(None, max_length=7)
    model_name: Optional[str] = Field(None, max_length=80)
    deleted_at: Optional[datetime] = None
    weigh: Optional[int] = None
    status: Optional[Literal['normal', 'hidden']] = Field(None, max_length=7)

    class Config:
        orm_mode = True

class SysUserRuleInDBBase(SysUserRuleBase):
    pass

class SysUserRule(SysUserRuleInDBBase):
    pass

