from datetime import datetime
from typing import Literal

from fastapi_babel import _
from pydantic import BaseModel, Field, field_validator


class SysAdminRuleBase(BaseModel):
    id: int | None = Field(None)
    rule_type: Literal["menu", "action"] = Field(..., max_length=6)
    parent_id: int | None = None
    name: str = Field(..., max_length=150)
    path: str = Field(..., max_length=50)
    component: str | None = None
    redirect: str | None = None
    meta: dict | None = None
    permission: dict | None = None
    menu_display_type: Literal["ajax", "addtabs", "blank", "dialog"] | None = None
    model_name: str = Field(..., max_length=80)
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None
    weigh: int = Field(...)
    status: Literal["normal", "hidden"] = Field(..., max_length=7)

    @field_validator("status")
    def validate_status(cls, v):
        if v not in ["normal", "hidden"]:
            raise ValueError(_("Input should be either normal or hidden"))
        return v

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class SysAdminRuleTree(SysAdminRuleBase):
    children: list["SysAdminRuleTree"] = []


# 解决递归引用的问题
SysAdminRuleTree.model_rebuild()


class SysAdminRuleCreate(SysAdminRuleBase):
    pass


class SysAdminRuleUpdate(BaseModel):
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


class SysAdminRuleInDBBase(SysAdminRuleBase):
    pass


class SysAdminRule(SysAdminRuleInDBBase):
    pass
