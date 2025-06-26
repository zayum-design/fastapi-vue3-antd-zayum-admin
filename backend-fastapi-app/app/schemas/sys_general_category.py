from datetime import datetime, date, timezone
from decimal import Decimal
from typing import Optional, Literal
from pydantic import BaseModel, Field, EmailStr, field_validator
from fastapi_babel import _
import re


class SysGeneralCategoryBase(BaseModel):
    id: int = Field(...)
    pid: int = Field(...)
    type: str = Field(Field(...), max_length=30)
    name: str = Field(Field(...), max_length=30)
    thumb: Optional[str] = None
    keywords: Optional[str] = None
    description: Optional[str] = None
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


class SysGeneralCategoryCreate(SysGeneralCategoryBase):
    id: Optional[int] = None
    pass

class SysGeneralCategoryUpdate(BaseModel):
    pid: Optional[int] = None
    type: Optional[str] = Field(None, max_length=30)
    name: Optional[str] = Field(None, max_length=30)
    thumb: Optional[str] = Field(None, max_length=100)
    keywords: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=255)
    weigh: Optional[int] = None
    status: Optional[Literal['normal', 'hidden']] = Field(None, max_length=6)

    class Config:
        orm_mode = True

class SysGeneralCategoryInDBBase(SysGeneralCategoryBase):
    id: int
    pid: Optional[int] = None
    type: Optional[str] = None
    name: Optional[str] = None
    thumb: Optional[str] = None
    keywords: Optional[str] = None
    description: Optional[str] = None
    weigh: Optional[int] = None
    status: Optional[Literal['normal', 'hidden']] = None

    class Config:
        orm_mode = True

class SysGeneralCategory(SysGeneralCategoryInDBBase):
    pass

