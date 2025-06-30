from datetime import datetime, date, timezone
from decimal import Decimal
from typing import Optional, Literal
from pydantic import BaseModel, Field, EmailStr, field_validator
from fastapi_babel import _
import re


class SysUserBalanceLogBase(BaseModel):
    id: Optional[int] = Field(None)
    user_id: int = Field(...)
    balance: Decimal = Field(...)
    before: Decimal = Field(...)
    after: Decimal = Field(...)
    memo: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True
        json_encoders = {
            Decimal: lambda v: str(v)
        }


class SysUserBalanceLogCreate(SysUserBalanceLogBase):
    pass

class SysUserBalanceLogUpdate(BaseModel):
    user_id: Optional[int] = None
    balance: Optional[Decimal] = None
    before: Optional[Decimal] = None
    after: Optional[Decimal] = None
    memo: Optional[str] = Field(None, max_length=255)

    class Config:
        orm_mode = True

class SysUserBalanceLogInDBBase(SysUserBalanceLogBase):
    pass

class SysUserBalanceLog(SysUserBalanceLogInDBBase):
    pass
