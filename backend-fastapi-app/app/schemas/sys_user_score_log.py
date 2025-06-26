from datetime import datetime, date, timezone
from decimal import Decimal
from typing import Optional, Literal
from pydantic import BaseModel, Field, EmailStr, field_validator
from fastapi_babel import _
import re


class SysUserScoreLogBase(BaseModel):
    id: int = Field(...)
    user_id: int = Field(...)
    score: int = Field(...)
    before: int = Field(...)
    after: int = Field(...)
    memo: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class SysUserScoreLogCreate(SysUserScoreLogBase):
    id: Optional[int] = None
    pass

class SysUserScoreLogUpdate(BaseModel):
    user_id: Optional[int] = None
    score: Optional[int] = None
    before: Optional[int] = None
    after: Optional[int] = None
    memo: Optional[str] = Field(None, max_length=255)

    class Config:
        orm_mode = True

class SysUserScoreLogInDBBase(SysUserScoreLogBase):
    id: int
    user_id: Optional[int] = None
    score: Optional[int] = None
    before: Optional[int] = None
    after: Optional[int] = None
    memo: Optional[str] = None

    class Config:
        orm_mode = True

class SysUserScoreLog(SysUserScoreLogInDBBase):
    pass

