from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field


class SysAttachmentBase(BaseModel):
    id: int | None = Field(None)
    cat_id: int | None = None
    admin_id: int = Field(...)
    user_id: int = Field(...)
    att_type: Literal["image", "file"] | None = None
    thumb: str | None = None
    path_file: str = Field(..., max_length=255)
    file_name: str | None = None
    file_size: int = Field(...)
    mimetype: str | None = None
    ext_param: str | None = None
    storage: str = Field(..., max_length=100)
    sha1: str | None = None
    general_attachment_col: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class SysAttachmentCreate(SysAttachmentBase):
    pass


class SysAttachmentUpdate(BaseModel):
    cat_id: int | None = None
    admin_id: int | None = None
    user_id: int | None = None
    att_type: Literal["image", "file"] | None = Field(None, max_length=5)
    thumb: str | None = Field(None, max_length=255)
    path_file: str | None = Field(None, max_length=255)
    file_name: str | None = Field(None, max_length=100)
    file_size: int | None = None
    mimetype: str | None = Field(None, max_length=100)
    ext_param: str | None = Field(None, max_length=255)
    storage: str | None = Field(None, max_length=100)
    sha1: str | None = Field(None, max_length=40)
    general_attachment_col: str | None = Field(None, max_length=45)

    class Config:
        from_attributes = True


class SysAttachmentInDBBase(SysAttachmentBase):
    pass


class SysAttachment(SysAttachmentInDBBase):
    pass
