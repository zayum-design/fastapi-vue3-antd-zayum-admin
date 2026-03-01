from datetime import datetime, date, timezone
from decimal import Decimal
from typing import Optional, Literal
from pydantic import BaseModel, Field, EmailStr, field_validator
from fastapi_babel import _
import re


class SysAttachmentBase(BaseModel):
    id: Optional[int] = Field(None)
    cat_id: Optional[int] = None
    admin_id: int = Field(...)
    user_id: int = Field(...)
    att_type: Optional[Literal['image', 'file']] = None
    thumb: Optional[str] = None
    path_file: str = Field(..., max_length=255)
    file_name: Optional[str] = None
    file_size: int = Field(...)
    mimetype: Optional[str] = None
    ext_param: Optional[str] = None
    storage: str = Field(..., max_length=100)
    sha1: Optional[str] = None
    general_attachment_col: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class SysAttachmentCreate(SysAttachmentBase):
    pass

class SysAttachmentUpdate(BaseModel):
    cat_id: Optional[int] = None
    admin_id: Optional[int] = None
    user_id: Optional[int] = None
    att_type: Optional[Literal['image', 'file']] = Field(None, max_length=5)
    thumb: Optional[str] = Field(None, max_length=255)
    path_file: Optional[str] = Field(None, max_length=255)
    file_name: Optional[str] = Field(None, max_length=100)
    file_size: Optional[int] = None
    mimetype: Optional[str] = Field(None, max_length=100)
    ext_param: Optional[str] = Field(None, max_length=255)
    storage: Optional[str] = Field(None, max_length=100)
    sha1: Optional[str] = Field(None, max_length=40)
    general_attachment_col: Optional[str] = Field(None, max_length=45)

    class Config:
        orm_mode = True

class SysAttachmentInDBBase(SysAttachmentBase):
    pass

class SysAttachment(SysAttachmentInDBBase):
    pass
