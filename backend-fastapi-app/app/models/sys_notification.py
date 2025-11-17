import re
import logging
import bcrypt
from typing import Literal, Optional
from datetime import date, datetime
from sqlalchemy import (
    FetchedValue, String, Integer, Boolean, DateTime, DECIMAL, SMALLINT, TEXT, DATE, DATETIME, UniqueConstraint, CheckConstraint, JSON, Enum, text
)
from sqlalchemy.orm import Mapped, mapped_column, validates
from .mixins import TimestampMixin
from app.models import Base
from fastapi_babel import _

logger = logging.getLogger(__name__)

# ENUM definitions
TypeEnum = Enum('system', 'message', 'comment', 'reminder', 'approval', 'security', 'update', 'task', name="type_enum", create_constraint=True)
StatusEnum = Enum('unread', 'read', name="status_enum", create_constraint=True)

class SysNotification(TimestampMixin, Base):
    __tablename__ = 'sys_notification'
    __table_args__ = ()

    id: Mapped[int] = mapped_column(Integer, nullable=False, primary_key=True, autoincrement=True)
    receiver_id: Mapped[int] = mapped_column(Integer, nullable=False)
    receiver_type: Mapped[str] = mapped_column(String(20), nullable=False, server_default=FetchedValue())

    @validates("receiver_type")
    def validate_receiver_type_length(self, key, value):
        if not value:
            raise ValueError(_("Value is required"))
        if len(value) > 20:
            logger.error(f"Value too long for {key}: {value} (max 20 chars)")
            raise ValueError(_(f"Value too long (max 20 characters)"))
        return value
                    
    sender_id: Mapped[int] = mapped_column(Integer, nullable=True)
    sender_name: Mapped[str] = mapped_column(String(50), nullable=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)

    @validates("title")
    def validate_title_length(self, key, value):
        if not value:
            raise ValueError(_("Value is required"))
        if len(value) > 100:
            logger.error(f"Value too long for {key}: {value} (max 100 chars)")
            raise ValueError(_(f"Value too long (max 100 characters)"))
        return value
                    
    message: Mapped[str] = mapped_column(TEXT, nullable=False)
    type: Mapped[Literal['system', 'message', 'comment', 'reminder', 'approval', 'security', 'update', 'task']] = mapped_column(TypeEnum, nullable=False, server_default=FetchedValue())
    status: Mapped[Literal['unread', 'read']] = mapped_column(StatusEnum, nullable=False, server_default=FetchedValue())
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    related_id: Mapped[int] = mapped_column(Integer, nullable=True)
    related_type: Mapped[str] = mapped_column(String(50), nullable=True)
    related_url: Mapped[str] = mapped_column(String(500), nullable=True)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, server_default=FetchedValue())
    expires_at: Mapped[datetime] = mapped_column(DATETIME, nullable=True)

    def __repr__(self):
        return f'<SysNotification(id={self.id})>'

    @classmethod
    def from_dict(cls, data: dict) -> 'SysNotification':
        valid_keys = {'sender_id', 'message', 'status', 'related_url', 'related_type', 'receiver_id', 'avatar', 'expires_at', 'title', 'id', 'related_id', 'sender_name', 'priority', 'receiver_type', 'type'}
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
    