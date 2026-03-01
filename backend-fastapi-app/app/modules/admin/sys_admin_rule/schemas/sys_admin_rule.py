from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, EmailStr, field_validator
from fastapi_babel import _
import re


class SysAdminRuleBase(BaseModel):
    id: Optional[int] = Field(None)
    rule_type: Literal['menu', 'action'] = Field(..., max_length=6)
    parent_id: Optional[int] = None
    name: str = Field(..., max_length=150)
    path: str = Field(..., max_length=50)
    component: Optional[str] = None
    redirect: Optional[str] = None
    meta: Optional[dict] = None
    permission: Optional[dict] = None
    menu_display_type: Optional[Literal['ajax', 'addtabs', 'blank', 'dialog']] = None
    model_name: str = Field(..., max_length=80)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    weigh: int = Field(...)
    status: Literal['normal', 'hidden'] = Field(..., max_length=7)

    @field_validator('status')
    def validate_status(cls, v):
        if v not in ['normal', 'hidden']:
            raise ValueError(_('Input should be either normal or hidden'))
        return v

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

class SysAdminRuleTree(SysAdminRuleBase):
    children: List['SysAdminRuleTree'] = []
# 解决递归引用的问题
SysAdminRuleTree.model_rebuild()

class SysAdminRuleCreate(SysAdminRuleBase):
    pass

class SysAdminRuleUpdate(BaseModel):
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
        from_attributes = True

class SysAdminRuleInDBBase(SysAdminRuleBase):
    pass

class SysAdminRule(SysAdminRuleInDBBase):
    pass
