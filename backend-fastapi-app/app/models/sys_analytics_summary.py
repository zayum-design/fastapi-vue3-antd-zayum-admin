import re
import logging
import bcrypt
from typing import Literal, Optional
from datetime import date, datetime
from sqlalchemy import (
    VARCHAR, FetchedValue, String, Integer,  DATE, JSON, Enum
)
from sqlalchemy.orm import Mapped, mapped_column, validates
from .mixins import TimestampMixin
from app.models import Base
from fastapi_babel import _

logger = logging.getLogger(__name__)

# ENUM definitions
Summary_typeEnum = Enum('daily', 'monthly', 'regional', name="summary_type_enum", create_constraint=True)

class SysAnalyticsSummary(TimestampMixin, Base):
    __tablename__ = 'sys_analytics_summary'
    __table_args__ = ()

    id: Mapped[str] = mapped_column(VARCHAR(200), nullable=False, primary_key=True)
    summary_type: Mapped[Literal['daily', 'monthly', 'regional']] = mapped_column(Summary_typeEnum, nullable=False)
    summary_date: Mapped[date] = mapped_column(DATE, nullable=True)
    summary_year: Mapped[int] = mapped_column(Integer, nullable=True)
    summary_month: Mapped[int] = mapped_column(Integer, nullable=True)
    region_name: Mapped[str] = mapped_column(String(100), nullable=True)
    total_users: Mapped[int] = mapped_column(Integer, nullable=True, server_default=FetchedValue())
    new_users: Mapped[int] = mapped_column(Integer, nullable=True, server_default=FetchedValue())
    active_users: Mapped[int] = mapped_column(Integer, nullable=True, server_default=FetchedValue())
    total_logins: Mapped[int] = mapped_column(Integer, nullable=True, server_default=FetchedValue())
    total_visits: Mapped[int] = mapped_column(Integer, nullable=True, server_default=FetchedValue())
    user_group_distribution: Mapped[dict] = mapped_column(JSON, nullable=True)
    action_distribution: Mapped[dict] = mapped_column(JSON, nullable=True)

    def __repr__(self):
        return f'<SysAnalyticsSummary(id={self.id})>'

    @classmethod
    def from_dict(cls, data: dict) -> 'SysAnalyticsSummary':
        valid_keys = {'summary_month', 'summary_type', 'total_visits', 'total_logins', 'total_users', 'region_name', 'id', 'summary_date', 'new_users', 'action_distribution', 'summary_year', 'user_group_distribution', 'active_users'}
        filtered_data = {key: value for key, value in data.items() if key in valid_keys}
        return cls(**filtered_data)
    


    def to_dict(self) -> dict:
        result_dict = {}
        for column in self.__table__.columns:
            if column.key in ['password', 'passwd', 'pwd']:
                continue
            value = getattr(self, column.key, None)
            result_dict[column.key] = value
        return result_dict
    