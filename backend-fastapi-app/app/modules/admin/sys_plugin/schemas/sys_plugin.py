from datetime import datetime
from decimal import Decimal
from typing import Literal

from fastapi_babel import _
from pydantic import BaseModel, Field, field_validator


class SysPluginBase(BaseModel):
    id: int | None = Field(None)
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
    created_at: datetime | None = None
    updated_at: datetime | None = None
    status: Literal["normal", "hidden"] = Field(..., max_length=6)

    @field_validator("status")
    def validate_status(cls, v):
        if v not in ["normal", "hidden"]:
            raise ValueError(_("Input should be either normal or hidden"))
        return v

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        json_encoders = {Decimal: lambda v: str(v)}


class SysPluginCreate(SysPluginBase):
    pass


class SysPluginUpdate(BaseModel):
    title: str | None = Field(None, max_length=120)
    author: str | None = Field(None, max_length=80)
    uuid: str | None = Field(None, max_length=120)
    description: str | None = Field(None, max_length=255)
    version: str | None = Field(None, max_length=50)
    downloads: int | None = None
    download_url: str | None = Field(None, max_length=255)
    md5_hash: str | None = Field(None, max_length=32)
    price: Decimal | None = None
    paid: int | None = None
    installed: int | None = None
    enabled: int | None = None
    setting_menu: str | None = Field(None, max_length=255)
    status: Literal["normal", "hidden"] | None = Field(None, max_length=6)

    class Config:
        from_attributes = True


class SysPluginInDBBase(SysPluginBase):
    pass


class SysPlugin(SysPluginInDBBase):
    pass
