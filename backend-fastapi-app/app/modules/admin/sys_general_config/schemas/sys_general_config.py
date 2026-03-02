from datetime import UTC, datetime

from pydantic import BaseModel, Field


class SysGeneralConfigBase(BaseModel):
    id: int | None = Field(None)
    name: str = Field(..., max_length=30)
    group: str = Field(..., max_length=30)
    title: str = Field(..., max_length=100)
    tip: str | None = None
    type: str | None = None
    visible: str | None = None
    value: str | None = None
    content: str | None = None
    rule: str | None = None
    extend: str | None = None
    setting: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class SysGeneralConfigCreate(SysGeneralConfigBase):
    pass


class SysGeneralConfigUpdate(BaseModel):
    name: str | None = Field(None, max_length=30)
    group: str | None = Field(None, max_length=30)
    title: str | None = Field(None, max_length=100)
    tip: str | None = Field(None, max_length=100)
    type: str | None = Field(None, max_length=30)
    visible: str | None = Field(None, max_length=255)
    value: str | None = Field(None)
    content: str | None = Field(None)
    rule: str | None = Field(None, max_length=100)
    extend: str | None = Field(None, max_length=255)
    setting: str | None = Field(None, max_length=255)

    class Config:
        from_attributes = True


class SysGeneralConfigInDBBase(SysGeneralConfigBase):
    pass


class SysGeneralConfig(SysGeneralConfigInDBBase):
    pass
