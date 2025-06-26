import re
import logging
from typing import Literal, Optional
from datetime import date, datetime
from sqlalchemy import String, Integer, TEXT, text
from sqlalchemy.orm import validates, Mapped, mapped_column
from .mixins import TimestampMixin
from app.models import Base
from fastapi_babel import _

logger = logging.getLogger(__name__)

# ENUM definitions

class SysGeneralConfig(TimestampMixin, Base):
    __tablename__ = 'sys_general_config'
    __table_args__ = ()

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(30))

    @validates("name")
    def validate_name(self, key, name):
        if not name:
            raise ValueError(_("Name is required"))
        if not re.match(r'^[\w\s\-\.]+$', name):
            logger.error(f"Invalid characters in name: {name}")
            raise ValueError(_("Name contains invalid characters"))
        if len(name) > 30:
            logger.error(f"Name too long: {name} (max 30 chars)")
            raise ValueError(_(f"Name too long (max 30 characters)"))
        return name
                
    group: Mapped[str] = mapped_column(String(30))

    @validates("group")
    def validate_group_length(self, key, value):
        if not value:
            raise ValueError(_("Value is required"))
        if len(value) > 30:
            logger.error(f"Value too long for {key}: {value} (max 30 chars)")
            raise ValueError(_(f"Value too long (max 30 characters)"))
        return value
                    
    title: Mapped[str] = mapped_column(String(100))

    @validates("title")
    def validate_title_length(self, key, value):
        if not value:
            raise ValueError(_("Value is required"))
        if len(value) > 100:
            logger.error(f"Value too long for {key}: {value} (max 100 chars)")
            raise ValueError(_(f"Value too long (max 100 characters)"))
        return value
                    
    tip: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    type: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    visible: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    value: Mapped[Optional[str]] = mapped_column(TEXT, nullable=True)
    content: Mapped[Optional[str]] = mapped_column(TEXT, nullable=True)
    rule: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    extend: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    setting: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    def __repr__(self):
        return f'<SysGeneralConfig(id={self.id})>'

    @classmethod
    def from_dict(cls, data: dict) -> 'SysGeneralConfig':
        valid_keys = {'id', 'group', 'type', 'visible', 'setting', 'tip', 'value', 'rule', 'extend', 'name', 'content', 'title'}
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
