from datetime import UTC, datetime

from pydantic import BaseModel, Field


class SysUserScoreLogBase(BaseModel):
    id: int | None = Field(None)
    user_id: int = Field(...)
    score: int = Field(...)
    before: int = Field(...)
    after: int = Field(...)
    memo: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class SysUserScoreLogCreate(SysUserScoreLogBase):
    pass


class SysUserScoreLogUpdate(BaseModel):
    user_id: int | None = None
    score: int | None = None
    before: int | None = None
    after: int | None = None
    memo: str | None = Field(None, max_length=255)

    class Config:
        from_attributes = True


class SysUserScoreLogInDBBase(SysUserScoreLogBase):
    pass


class SysUserScoreLog(SysUserScoreLogInDBBase):
    pass
