import logging
import re
from typing import Literal

from fastapi_babel import _
from sqlalchemy import JSON, Enum, FetchedValue, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, validates

from app.core.mixins import TimestampMixin
from app.core.models import Base

logger = logging.getLogger(__name__)

# ENUM definitions
StatusEnum = Enum("normal", "hidden", name="status_enum", create_constraint=True)


class SysUserGroup(TimestampMixin, Base):
    __tablename__ = "sys_user_group"
    __table_args__ = ()

    id: Mapped[int] = mapped_column(Integer, nullable=False, primary_key=True, autoincrement=True)
    pid: Mapped[int] = mapped_column(Integer, nullable=False, server_default=FetchedValue())
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    @validates("name")
    def validate_name(self, key, name):
        if not name:
            raise ValueError(_("Name is required"))
        if not re.match(r"^[\w\s\-\.]+$", name):
            logger.error("Invalid characters in name: {name}")
            raise ValueError(_("Name contains invalid characters"))
        if len(name) > 100:
            logger.error("Name too long: {name} (max 100 chars)")
            raise ValueError(_("Name too long (max 100 characters)"))
        return name

    rules: Mapped[dict] = mapped_column(JSON, nullable=False)
    access: Mapped[dict] = mapped_column(JSON, nullable=False)
    status: Mapped[Literal["normal", "hidden"]] = mapped_column(
        StatusEnum, nullable=False, server_default=FetchedValue()
    )

    def __repr__(self):
        return f"<SysUserGroup(id={self.id})>"

    @classmethod
    def from_dict(cls, data: dict) -> "SysUserGroup":
        valid_keys = {"id", "status", "name", "rules", "access", "pid"}
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
