from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Literal
from pydantic import BaseModel, Field, EmailStr, field_validator
from fastapi_babel import _
import re


class SysPluginBase(BaseModel):
    id: Optional[int] = Field(None)
    title: str = Field(..., max_length=120)
    author: str = Field(..., max_length=80)
    uuid: str = Field(..., max_length=120)
    description: str = Field(..., max_length=255)
    version: str = Field(..., max_length=50)
    downloads: int = Field(...)
    download_url: str = Field(..., max_length=255)
    md5_hash: str = Field(..., max_length=32)
    price: Decimal = Field(...)
    paid: int = Field(...)
    installed: int = Field(...)
    enabled: int = Field(...)
    setting_menu: str = Field(..., max_length=255)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    status: Literal['normal', 'hidden'] = Field(..., max_length=6)

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
    pass

class SysPlugin(SysPluginInDBBase):
    pass
