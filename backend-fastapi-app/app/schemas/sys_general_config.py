from datetime import datetime, date, timezone
from decimal import Decimal
from typing import Optional, Literal
from pydantic import BaseModel, Field, EmailStr, field_validator
from fastapi_babel import _
import re


class SysGeneralConfigBase(BaseModel):
    id: int = Field(...)
    name: str = Field(Field(...), max_length=30)
    group: str = Field(Field(...), max_length=30)
    title: str = Field(Field(...), max_length=100)
    tip: Optional[str] = None
    type: Optional[str] = None
    visible: Optional[str] = None
    value: Optional[str] = None
    content: Optional[str] = None
    rule: Optional[str] = None
    extend: Optional[str] = None
    setting: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class SysGeneralConfigCreate(SysGeneralConfigBase):
    id: Optional[int] = None
    pass

class SysGeneralConfigUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=30)
    group: Optional[str] = Field(None, max_length=30)
    title: Optional[str] = Field(None, max_length=100)
    tip: Optional[str] = Field(None, max_length=100)
    type: Optional[str] = Field(None, max_length=30)
    visible: Optional[str] = Field(None, max_length=255)
    value: Optional[str] = Field(None)
    content: Optional[str] = Field(None)
    rule: Optional[str] = Field(None, max_length=100)
    extend: Optional[str] = Field(None, max_length=255)
    setting: Optional[str] = Field(None, max_length=255)

    class Config:
        orm_mode = True

class SysGeneralConfigInDBBase(SysGeneralConfigBase):
    id: int
    name: Optional[str] = None
    group: Optional[str] = None
    title: Optional[str] = None
    tip: Optional[str] = None
    type: Optional[str] = None
    visible: Optional[str] = None
    value: Optional[str] = None
    content: Optional[str] = None
    rule: Optional[str] = None
    extend: Optional[str] = None
    setting: Optional[str] = None

    class Config:
        orm_mode = True

class SysGeneralConfig(SysGeneralConfigInDBBase):
    pass

