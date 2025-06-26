import re
import logging
from typing import Literal, Optional
from datetime import date, datetime
from sqlalchemy import String, text, TEXT
from sqlalchemy.orm import validates, Mapped, mapped_column
from .mixins import TimestampMixin
from app.models import Base
from fastapi_babel import _

logger = logging.getLogger(__name__)

# ENUM definitions

class SysAdminLog(TimestampMixin, Base):
    __tablename__ = 'sys_admin_log'
    __table_args__ = ()

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    admin_id: Mapped[int] = mapped_column()
    username: Mapped[str] = mapped_column(String(30))

    @validates("username")
    def validate_username(self, key, username):
        if not username:
            raise ValueError(_("Username is required"))
        if not username.isalnum():
            logger.error(f"Username contains non-alphanumeric characters: {username}")
            raise ValueError(_("Username must be alphanumeric"))
        if len(username) > 30:
            logger.error(f"Username too long: {username} (max 30 chars)")
            raise ValueError(_(f"Username too long (max 30 characters)"))
        return username
                
    url: Mapped[str] = mapped_column(String(1500))

    @validates("url")
    def validate_url(self, key, url):
        if not url:
            raise ValueError(_("URL is required"))
        if not (url.startswith('http://') or url.startswith('https://')):
            logger.error(f"Invalid URL format: {url}")
            raise ValueError(_("URL must start with http:// or https://"))
        if len(url) > 1500:
            logger.error(f"URL too long: {url} (max 1500 chars)")
            raise ValueError(_(f"URL too long (max 1500 characters)"))
        return url
                
    title: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    content: Mapped[str] = mapped_column(TEXT)
    ip: Mapped[str] = mapped_column(String(50))

    @validates("ip")
    def validate_ip_length(self, key, value):
        if not value:
            raise ValueError(_("Value is required"))
        if len(value) > 50:
            logger.error(f"Value too long for {key}: {value} (max 50 chars)")
            raise ValueError(_(f"Value too long (max 50 characters)"))
        return value
                    
    useragent: Mapped[Optional[str]] = mapped_column(TEXT, nullable=True)

    def __repr__(self):
        return f'<SysAdminLog(id={self.id})>'

    @classmethod
    def from_dict(cls, data: dict) -> 'SysAdminLog':
        valid_keys = {'username', 'url', 'useragent', 'ip', 'title', 'admin_id', 'content', 'id'}
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
