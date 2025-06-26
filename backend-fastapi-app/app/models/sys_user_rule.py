import re
import logging
from typing import Literal, Optional
from datetime import date, datetime
from sqlalchemy import String, Integer, SMALLINT, text, Enum
from sqlalchemy.orm import validates, Mapped, mapped_column
from .mixins import TimestampMixin
from app.models import Base
from fastapi_babel import _

logger = logging.getLogger(__name__)

# ENUM definitions
TypeEnum = Enum('menu', 'action', name="type_enum", create_constraint=True)
MenutypeEnum = Enum('addtabs', 'blank', 'dialog', 'ajax',
                    name="menutype_enum", create_constraint=True)
StatusEnum = Enum('normal', 'hidden', name="status_enum",
                  create_constraint=True)


class SysUserRule(TimestampMixin, Base):
    __tablename__ = 'sys_user_rule'
    __table_args__ = ()

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(TypeEnum)
    pid: Mapped[int] = mapped_column()
    plugin: Mapped[int] = mapped_column(SMALLINT)
    name: Mapped[str] = mapped_column(String(150))

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

    path: Mapped[str] = mapped_column(String(50))

    @validates("path")
    def validate_path(self, key, path):
        if not path:
            raise ValueError(_("Path is required"))
        if len(path) > 50:
            logger.error(f"Path too long: {path} (max 50 chars)")
            raise ValueError(_(f"Path too long (max 50 characters)"))
        return path

    title: Mapped[str] = mapped_column(String(50))

    @validates("title")
    def validate_title(self, key, title):
        if not title:
            raise ValueError(_("Title is required"))
        if len(title) > 50:
            logger.error(f"Title too long: {title} (max 50 chars)")
            raise ValueError(_(f"Title too long (max 50 characters)"))
        return title

    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    icon: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    menutype: Mapped[Optional[str]] = mapped_column(MenutypeEnum, nullable=True)
    extend: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    model_name: Mapped[str] = mapped_column(String(50))

    @validates("model_name")
    def validate_model_name(self, key, name):
        if not name:
            raise ValueError(_("Name is required"))
        if not re.match(r'^[\w\s\-\.]+$', name):
            logger.error(f"Invalid characters in name: {name}")
            raise ValueError(_("Name contains invalid characters"))
        if len(name) > 50:
            logger.error(f"Name too long: {name} (max 50 chars)")
            raise ValueError(_(f"Name too long (max 50 characters)"))
        return name

    weigh: Mapped[int] = mapped_column()
    status: Mapped[str] = mapped_column(StatusEnum, server_default=text("'normal'"))

    def __repr__(self):
        return f'<SysUserRule(id={self.id})>'

    @classmethod
    def from_dict(cls, data: dict) -> 'SysUserRule':
        valid_keys = {'path', 'name', 'type', 'icon', 'extend', 'title', 'menutype',
                      'plugin', 'weigh', 'status', 'model_name', 'description', 'id', 'pid'}
        filtered_data = {key: value for key,
                         value in data.items() if key in valid_keys}
        return cls(**filtered_data)

    def to_dict(self) -> dict:
        result_dict = {}
        for column in self.__table__.columns:
            if column.key in ['password', 'passwd', 'pwd']:
                continue
            value = getattr(self, column.key, None)
            result_dict[column.key] = value
        return result_dict
