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
Att_typeEnum = Enum('image', 'file', name="att_type_enum", create_constraint=True)

class SysAttachment(TimestampMixin, Base):
    __tablename__ = 'sys_attachment'
    __table_args__ = ()

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cat_id: Mapped[int] = mapped_column(server_default=text("'0'"), nullable=True)
    admin_id: Mapped[int] = mapped_column()
    user_id: Mapped[int] = mapped_column()
    att_type: Mapped[Optional[str]] = mapped_column(Att_typeEnum, server_default=text("'image'"), nullable=True)
    thumb: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    path_file: Mapped[str] = mapped_column(String(255))
    file_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    file_size: Mapped[int] = mapped_column()
    mimetype: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    ext_param: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    storage: Mapped[str] = mapped_column(String(100))

    @validates("storage")
    def validate_storage_length(self, key, value):
        if not value:
            raise ValueError(_("Value is required"))
        if len(value) > 100:
            logger.error(f"Value too long for {key}: {value} (max 100 chars)")
            raise ValueError(_(f"Value too long (max 100 characters)"))
        return value
                    
    sha1: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    general_attachment_col: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)

    def __repr__(self):
        return f'<SysAttachment(id={self.id})>'

    @classmethod
    def from_dict(cls, data: dict) -> 'SysAttachment':
        valid_keys = {'id', 'general_attachment_col', 'admin_id', 'ext_param', 'user_id', 'thumb', 'cat_id', 'file_name', 'storage', 'path_file', 'file_size', 'sha1', 'att_type', 'mimetype'}
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
