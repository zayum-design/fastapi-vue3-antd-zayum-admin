from datetime import UTC, date, datetime
from typing import Literal

from pydantic import BaseModel, Field


class SysAnalyticsSummaryBase(BaseModel):
    id: str = Field(..., max_length=200)
    summary_type: Literal["daily", "monthly", "regional"] = Field(..., max_length=8)
    summary_date: date | None = None
    summary_year: int | None = None
    summary_month: int | None = None
    region_name: str | None = None
    total_users: int | None = None
    new_users: int | None = None
    active_users: int | None = None
    total_logins: int | None = None
    total_visits: int | None = None
    user_group_distribution: dict | None = None
    action_distribution: dict | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class SysAnalyticsSummaryCreate(SysAnalyticsSummaryBase):
    pass


class SysAnalyticsSummaryUpdate(BaseModel):
    summary_type: Literal["daily", "monthly", "regional"] | None = Field(None, max_length=8)
    summary_date: date | None = None
    summary_year: int | None = None
    summary_month: int | None = None
    region_name: str | None = Field(None, max_length=100)
    total_users: int | None = None
    new_users: int | None = None
    active_users: int | None = None
    total_logins: int | None = None
    total_visits: int | None = None
    user_group_distribution: dict | None = None
    action_distribution: dict | None = None

    class Config:
        from_attributes = True


class SysAnalyticsSummaryInDBBase(SysAnalyticsSummaryBase):
    pass


class SysAnalyticsSummary(SysAnalyticsSummaryInDBBase):
    pass
