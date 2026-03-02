from datetime import UTC, datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class SysUserBalanceLogBase(BaseModel):
    id: int | None = Field(None)
    user_id: int = Field(...)
    balance: Decimal = Field(...)
    before: Decimal = Field(...)
    after: Decimal = Field(...)
    memo: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        json_encoders = {Decimal: lambda v: str(v)}


class SysUserBalanceLogCreate(SysUserBalanceLogBase):
    pass


class SysUserBalanceLogUpdate(BaseModel):
    user_id: int | None = None
    balance: Decimal | None = None
    before: Decimal | None = None
    after: Decimal | None = None
    memo: str | None = Field(None, max_length=255)

    class Config:
        from_attributes = True


class SysUserBalanceLogInDBBase(SysUserBalanceLogBase):
    pass


class SysUserBalanceLog(SysUserBalanceLogInDBBase):
    pass
