from datetime import UTC, datetime
from typing import Literal

from fastapi_babel import _
from pydantic import BaseModel, Field, field_validator


class SysUserRuleBase(BaseModel):
    id: int = Field(...)
    rule_type: Literal["menu", "action"] = Field(Field(...), max_length=6)
    parent_id: int = Field(...)
    name: str = Field(Field(...), max_length=150)
    path: str = Field(Field(...), max_length=50)
    component: str | None = None
    redirect: str | None = None
    meta: dict | None = None
    permission: dict | None = None
    menu_display_type: Literal["ajax", "addtabs", "blank", "dialog"] | None = None
    model_name: str = Field(Field(...), max_length=80)
    deleted_at: datetime | None = None
    weigh: int = Field(...)
    status: Literal["normal", "hidden"] = Field(Field(...), max_length=7)
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


class SysUserRuleCreate(SysUserRuleBase):
    pass


class SysUserRuleUpdate(BaseModel):
    rule_type: Literal["menu", "action"] | None = Field(None, max_length=6)
    parent_id: int | None = None
    name: str | None = Field(None, max_length=150)
    path: str | None = Field(None, max_length=50)
    component: str | None = Field(None, max_length=200)
    redirect: str | None = Field(None, max_length=100)
    meta: dict | None = None
    permission: dict | None = None
    menu_display_type: Literal["ajax", "addtabs", "blank", "dialog"] | None = Field(
        None, max_length=7
    )
    model_name: str | None = Field(None, max_length=80)
    deleted_at: datetime | None = None
    weigh: int | None = None
    status: Literal["normal", "hidden"] | None = Field(None, max_length=7)

    class Config:
        from_attributes = True


class SysUserRuleInDBBase(SysUserRuleBase):
    pass


class SysUserRule(SysUserRuleInDBBase):
    pass
