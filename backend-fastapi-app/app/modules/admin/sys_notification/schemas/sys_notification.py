from datetime import UTC, datetime
from typing import Literal

from fastapi_babel import _
from pydantic import BaseModel, Field, field_validator


class SysNotificationBase(BaseModel):
    id: int = Field(...)
    receiver_id: int = Field(...)
    receiver_type: str = Field(Field(...), max_length=20)
    sender_id: int | None = None
    sender_name: str | None = None
    title: str = Field(Field(...), max_length=100)
    message: str = Field(Field(...))
    type: Literal[
        "system", "message", "comment", "reminder", "approval", "security", "update", "task"
    ] = Field(Field(...), max_length=8)
    status: Literal["normal", "hidden"] = Field(Field(...), max_length=6)
    avatar: str | None = None
    related_id: int | None = None
    related_type: str | None = None
    related_url: str | None = None
    priority: int = Field(...)
    expires_at: datetime | None = None
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


class SysNotificationCreate(SysNotificationBase):
    pass


class SysNotificationUpdate(BaseModel):
    receiver_id: int | None = None
    receiver_type: str | None = Field(None, max_length=20)
    sender_id: int | None = None
    sender_name: str | None = Field(None, max_length=50)
    title: str | None = Field(None, max_length=100)
    message: str | None = Field(None)
    type: (
        Literal[
            "system", "message", "comment", "reminder", "approval", "security", "update", "task"
        ]
        | None
    ) = Field(None, max_length=8)
    status: Literal["normal", "hidden"] | None = Field(None, max_length=6)
    avatar: str | None = Field(None, max_length=255)
    related_id: int | None = None
    related_type: str | None = Field(None, max_length=50)
    related_url: str | None = Field(None, max_length=500)
    priority: int | None = None
    expires_at: datetime | None = None

    class Config:
        from_attributes = True


class SysNotificationInDBBase(SysNotificationBase):
    pass


class SysNotification(SysNotificationInDBBase):
    pass
