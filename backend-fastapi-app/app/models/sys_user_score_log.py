import re
import logging
from typing import Literal, Optional
from datetime import date, datetime
from sqlalchemy import String, Integer, text
from sqlalchemy.orm import validates, Mapped, mapped_column
from .mixins import TimestampMixin
from app.models import Base
from fastapi_babel import _

logger = logging.getLogger(__name__)

# ENUM definitions

class SysUserScoreLog(TimestampMixin, Base):
    __tablename__ = 'sys_user_score_log'
    __table_args__ = ()

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column()
    score: Mapped[int] = mapped_column()
    before: Mapped[int] = mapped_column()
    after: Mapped[int] = mapped_column()
    memo: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    def __repr__(self):
        return f'<SysUserScoreLog(id={self.id})>'

    @classmethod
    def from_dict(cls, data: dict) -> 'SysUserScoreLog':
        valid_keys = {'before', 'memo', 'user_id', 'after', 'score', 'id'}
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
