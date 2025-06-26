from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Literal
from pydantic import BaseModel, Field, EmailStr, field_validator
from fastapi_babel import _
import re


class SysPluginBase(BaseModel):
    id: int = Field(...)
    title: str = Field(Field(...), max_length=120)
    author: str = Field(Field(...), max_length=80)
    uuid: str = Field(Field(...), max_length=120)
    description: str = Field(Field(...), max_length=255)
    version: str = Field(Field(...), max_length=50)
    downloads: int = Field(...)
    download_url: str = Field(Field(...), max_length=255)
    md5_hash: str = Field(Field(...), max_length=32)
    price: Decimal = Field(...)
    paid: int = Field(...)
    installed: int = Field(...)
    enabled: int = Field(...)
    setting_menu: str = Field(Field(...), max_length=255)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    status: Literal['normal', 'hidden'] = Field(Field(...), max_length=6)

    @field_validator('status')
    def validate_status(cls, v):
        if v not in ['normal', 'hidden']:
            raise ValueError(_('Input should be either normal or hidden'))
        return v

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True
        json_encoders = {
            Decimal: lambda v: str(v)
        }


class SysPluginCreate(SysPluginBase):
    id: Optional[int] = None
    pass

class SysPluginUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=120)
    author: Optional[str] = Field(None, max_length=80)
    uuid: Optional[str] = Field(None, max_length=120)
    description: Optional[str] = Field(None, max_length=255)
    version: Optional[str] = Field(None, max_length=50)
    downloads: Optional[int] = None
    download_url: Optional[str] = Field(None, max_length=255)
    md5_hash: Optional[str] = Field(None, max_length=32)
    price: Optional[Decimal] = None
    paid: Optional[int] = None
    installed: Optional[int] = None
    enabled: Optional[int] = None
    setting_menu: Optional[str] = Field(None, max_length=255)
    status: Optional[Literal['normal', 'hidden']] = Field(None, max_length=6)

    class Config:
        orm_mode = True

class SysPluginInDBBase(SysPluginBase):
    id: int
    title: Optional[str] = None
    author: Optional[str] = None
    uuid: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    downloads: Optional[int] = None
    download_url: Optional[str] = None
    md5_hash: Optional[str] = None
    price: Optional[Decimal] = None
    paid: Optional[int] = None
    installed: Optional[int] = None
    enabled: Optional[int] = None
    setting_menu: Optional[str] = None
    status: Optional[Literal['normal', 'hidden']] = None

    class Config:
        orm_mode = True

class SysPlugin(SysPluginInDBBase):
    pass

