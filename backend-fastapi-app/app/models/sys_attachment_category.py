import re
import logging
from typing import Literal, Optional
from datetime import date, datetime
from sqlalchemy import String, Integer, text, Enum
from sqlalchemy.orm import validates, Mapped, mapped_column
from .mixins import TimestampMixin
from app.models import Base
from fastapi_babel import _

logger = logging.getLogger(__name__)

# ENUM definitions
StatusEnum = Enum('normal', 'hidden', name="status_enum", create_constraint=True)

class SysAttachmentCategory(TimestampMixin, Base):
    __tablename__ = 'sys_attachment_category'
    __table_args__ = ()

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    pid: Mapped[int] = mapped_column(server_default=text("'0'"))
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
                
    status: Mapped[str] = mapped_column(StatusEnum)

    def __repr__(self):
        return f'<SysAttachmentCategory(id={self.id})>'

    @classmethod
    def from_dict(cls, data: dict) -> 'SysAttachmentCategory':
        valid_keys = {'pid', 'id', 'name', 'status'}
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
