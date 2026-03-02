import logging
import re

from fastapi_babel import _
from sqlalchemy import TEXT, String
from sqlalchemy.orm import Mapped, mapped_column, validates

from app.core.mixins import TimestampMixin
from app.core.models import Base

logger = logging.getLogger(__name__)

# ENUM definitions


class SysGeneralConfig(TimestampMixin, Base):
    __tablename__ = "sys_general_config"
    __table_args__ = ()

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(30))

    @validates("name")
    def validate_name(self, key, name):
        if not name:
            raise ValueError(_("Name is required"))
        if not re.match(r"^[\w\s\-\.]+$", name):
            logger.error("Invalid characters in name: {name}")
            raise ValueError(_("Name contains invalid characters"))
        if len(name) > 30:
            logger.error("Name too long: {name} (max 30 chars)")
            raise ValueError(_("Name too long (max 30 characters)"))
        return name

    group: Mapped[str] = mapped_column(String(30))

    @validates("group")
    def validate_group_length(self, key, value):
        if not value:
            raise ValueError(_("Value is required"))
        if len(value) > 30:
            logger.error("Value too long for {key}: {value} (max 30 chars)")
            raise ValueError(_("Value too long (max 30 characters)"))
        return value

    title: Mapped[str] = mapped_column(String(100))

    @validates("title")
    def validate_title_length(self, key, value):
        if not value:
            raise ValueError(_("Value is required"))
        if len(value) > 100:
            logger.error("Value too long for {key}: {value} (max 100 chars)")
            raise ValueError(_("Value too long (max 100 characters)"))
        return value

    tip: Mapped[str | None] = mapped_column(String(100), nullable=True)
    type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    visible: Mapped[str | None] = mapped_column(String(255), nullable=True)
    value: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    content: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    rule: Mapped[str | None] = mapped_column(String(100), nullable=True)
    extend: Mapped[str | None] = mapped_column(String(255), nullable=True)
    setting: Mapped[str | None] = mapped_column(String(255), nullable=True)

    def __repr__(self):
        return f"<SysGeneralConfig(id={self.id})>"

    @classmethod
    def from_dict(cls, data: dict) -> "SysGeneralConfig":
        valid_keys = {
            "id",
            "group",
            "type",
            "visible",
            "setting",
            "tip",
            "value",
            "rule",
            "extend",
            "name",
            "content",
            "title",
        }
        filtered_data = {key: value for key, value in data.items() if key in valid_keys}
        return cls(**filtered_data)

    def to_dict(self) -> dict:
        result_dict = {}
        for column in self.__table__.columns:
            if column.key in ["password", "passwd", "pwd"]:
                continue
            value = getattr(self, column.key, None)
            result_dict[column.key] = value
        return result_dict
