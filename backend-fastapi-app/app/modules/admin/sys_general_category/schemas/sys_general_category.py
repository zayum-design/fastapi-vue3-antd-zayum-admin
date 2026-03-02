from datetime import UTC, datetime
from typing import Literal

from fastapi_babel import _
from pydantic import BaseModel, Field, field_validator


class SysGeneralCategoryBase(BaseModel):
    id: int | None = Field(None)
    pid: int = Field(...)
    type: str = Field(..., max_length=30)
    name: str = Field(..., max_length=30)
    thumb: str | None = None
    keywords: str | None = None
    description: str | None = None
    weigh: int = Field(...)
    status: Literal["normal", "hidden"] = Field(..., max_length=6)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("status")
    def validate_status(cls, v):
        if v not in ["normal", "hidden"]:
            raise ValueError(_("STATUS should be either normal or hidden"))
        return v

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class SysGeneralCategoryCreate(SysGeneralCategoryBase):
    pass


class SysGeneralCategoryUpdate(BaseModel):
    pid: int | None = None
    type: str | None = Field(None, max_length=30)
    name: str | None = Field(None, max_length=30)
    thumb: str | None = Field(None, max_length=100)
    keywords: str | None = Field(None, max_length=255)
    description: str | None = Field(None, max_length=255)
    weigh: int | None = None
    status: Literal["normal", "hidden"] | None = Field(None, max_length=6)

    class Config:
        from_attributes = True


class SysGeneralCategoryInDBBase(SysGeneralCategoryBase):
    pass


class SysGeneralCategory(SysGeneralCategoryInDBBase):
    pass
