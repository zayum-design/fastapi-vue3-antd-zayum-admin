from datetime import datetime, date, timezone
from decimal import Decimal
from typing import Optional, Literal
from pydantic import BaseModel, Field, EmailStr, field_validator
from fastapi_babel import _
import re


class SysAnalyticsSummaryBase(BaseModel):
    id: str = Field(..., max_length=200)
    summary_type: Literal['daily', 'monthly', 'regional'] = Field(..., max_length=8)
    summary_date: Optional[date] = None
    summary_year: Optional[int] = None
    summary_month: Optional[int] = None
    region_name: Optional[str] = None
    total_users: Optional[int] = None
    new_users: Optional[int] = None
    active_users: Optional[int] = None
    total_logins: Optional[int] = None
    total_visits: Optional[int] = None
    user_group_distribution: Optional[dict] = None
    action_distribution: Optional[dict] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class SysAnalyticsSummaryCreate(SysAnalyticsSummaryBase):
    pass

class SysAnalyticsSummaryUpdate(BaseModel):
    summary_type: Optional[Literal['daily', 'monthly', 'regional']] = Field(None, max_length=8)
    summary_date: Optional[date] = None
    summary_year: Optional[int] = None
    summary_month: Optional[int] = None
    region_name: Optional[str] = Field(None, max_length=100)
    total_users: Optional[int] = None
    new_users: Optional[int] = None
    active_users: Optional[int] = None
    total_logins: Optional[int] = None
    total_visits: Optional[int] = None
    user_group_distribution: Optional[dict] = None
    action_distribution: Optional[dict] = None

    class Config:
        orm_mode = True

class SysAnalyticsSummaryInDBBase(SysAnalyticsSummaryBase):
    pass

class SysAnalyticsSummary(SysAnalyticsSummaryInDBBase):
    pass
