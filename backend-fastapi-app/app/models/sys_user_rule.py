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
Rule_typeEnum = Enum('menu', 'action', name="rule_type_enum", create_constraint=True)
Menu_display_typeEnum = Enum('ajax', 'addtabs', 'blank', 'dialog', name="menu_display_type_enum", create_constraint=True)
StatusEnum = Enum('normal', 'hidden', 'deleted', name="status_enum", create_constraint=True)

class SysUserRule(TimestampMixin, Base):
    __tablename__ = 'sys_user_rule'
    __table_args__ = ()

    id: Mapped[int] = mapped_column(Integer, nullable=False, primary_key=True, autoincrement=True)
    rule_type: Mapped[Literal['menu', 'action']] = mapped_column(Rule_typeEnum, nullable=False, server_default=FetchedValue())
    parent_id: Mapped[int] = mapped_column(Integer, nullable=False, server_default=FetchedValue())
    name: Mapped[str] = mapped_column(String(150), nullable=False)

    @validates("name")
    def validate_name(self, key, name):
        if not name:
            raise ValueError(_("Name is required"))
        if not re.match(r'^[\w\s\-\.]+$', name):
            logger.error(f"Invalid characters in name: {name}")
            raise ValueError(_("Name contains invalid characters"))
        if len(name) > 150:
            logger.error(f"Name too long: {name} (max 150 chars)")
            raise ValueError(_(f"Name too long (max 150 characters)"))
        return name
                
    path: Mapped[str] = mapped_column(String(50), nullable=False)

    @validates("path")
    def validate_path_length(self, key, value):
        if not value:
            raise ValueError(_("Value is required"))
        if len(value) > 50:
            logger.error(f"Value too long for {key}: {value} (max 50 chars)")
            raise ValueError(_(f"Value too long (max 50 characters)"))
        return value
                    
    component: Mapped[str] = mapped_column(String(200), nullable=True)
    redirect: Mapped[str] = mapped_column(String(100), nullable=True)
    meta: Mapped[dict] = mapped_column(JSON, nullable=True)
    permission: Mapped[dict] = mapped_column(JSON, nullable=True)
    menu_display_type: Mapped[Literal['ajax', 'addtabs', 'blank', 'dialog']] = mapped_column(Menu_display_typeEnum, nullable=True, server_default=FetchedValue())
    model_name: Mapped[str] = mapped_column(String(80), nullable=False)

    @validates("model_name")
    def validate_model_name(self, key, name):
        if not name:
            raise ValueError(_("Name is required"))
        if not re.match(r'^[\w\s\-\.]+$', name):
            logger.error(f"Invalid characters in name: {name}")
            raise ValueError(_("Name contains invalid characters"))
        if len(name) > 80:
            logger.error(f"Name too long: {name} (max 80 chars)")
            raise ValueError(_(f"Name too long (max 80 characters)"))
        return name
                
    deleted_at: Mapped[datetime] = mapped_column(DATETIME, nullable=True)
    weigh: Mapped[int] = mapped_column(Integer, nullable=False, server_default=FetchedValue())
    status: Mapped[Literal['normal', 'hidden', 'deleted']] = mapped_column(StatusEnum, nullable=False, server_default=FetchedValue())

    def __repr__(self):
        return f'<SysUserRule(id={self.id})>'

    @classmethod
    def from_dict(cls, data: dict) -> 'SysUserRule':
        valid_keys = {'rule_type', 'model_name', 'status', 'component', 'redirect', 'meta', 'permission', 'path', 'menu_display_type', 'name', 'deleted_at', 'weigh', 'id', 'parent_id'}
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
    