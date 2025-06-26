import re
import logging
import bcrypt
from typing import Literal, Optional
from datetime import date, datetime
from sqlalchemy import String, text, Enum
from sqlalchemy.orm import validates, Mapped, mapped_column
from .mixins import TimestampMixin
from app.models import Base
from fastapi_babel import _

logger = logging.getLogger(__name__)

# ENUM definitions
StatusEnum = Enum('normal', 'hidden', name="status_enum", create_constraint=True)

class SysAdmin(TimestampMixin, Base):
    __tablename__ = 'sys_admin'
    __table_args__ = ()

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(server_default=text("'1'"))
    username: Mapped[str] = mapped_column(String(20))

    @validates("username")
    def validate_username(self, key, username):
        if not username:
            raise ValueError(_("Username is required"))
        if not username.isalnum():
            logger.error(f"Username contains non-alphanumeric characters: {username}")
            raise ValueError(_("Username must be alphanumeric"))
        if len(username) > 20:
            logger.error(f"Username too long: {username} (max 20 chars)")
            raise ValueError(_(f"Username too long (max 20 characters)"))
        return username
                
    nickname: Mapped[str] = mapped_column(String(50))

    @validates("nickname")
    def validate_nickname(self, key, name):
        if not name:
            raise ValueError(_("Name is required"))
        if not re.match(r'^[\w\s\-\.]+$', name):
            logger.error(f"Invalid characters in name: {name}")
            raise ValueError(_("Name contains invalid characters"))
        if len(name) > 50:
            logger.error(f"Name too long: {name} (max 50 chars)")
            raise ValueError(_(f"Name too long (max 50 characters)"))
        return name
                
    _password: Mapped[Optional[str]] = mapped_column('password', String(128), nullable=True)

    @validates("_password")
    def validate__password_length(self, key, value):
        if not value:
            raise ValueError(_("Value is required"))
        if len(value) > 128:
            logger.error(f"Value too long for {key}: {value} (max 128 chars)")
            raise ValueError(_(f"Value too long (max 128 characters)"))
        return value
                    
    avatar: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    email: Mapped[str] = mapped_column(String(100))

    @validates("email")
    def validate_email(self, key, address):
        if not address:
            raise ValueError(_("Email is required"))
        if "@" not in address:
            logger.error(f"Invalid email address provided: {address}")
            raise ValueError(_("Invalid email address"))
        if len(address) > 100:
            logger.error(f"Email too long: {address} (max 100 chars)")
            raise ValueError(_(f"Email too long (max 100 characters)"))
        return address
                
    mobile: Mapped[str] = mapped_column(String(11))

    @validates("mobile")
    def validate_mobile(self, key, mobile):
        if not mobile:
            raise ValueError(_("Mobile number is required"))
        if not mobile.isdigit():
            logger.error(f"Mobile number contains non-digit characters: {mobile}")
            raise ValueError(_("Mobile number must contain only digits"))
        if len(mobile) != 11:
            logger.error(f"Mobile number length is not 11 digits: {mobile}")
            raise ValueError(_("Mobile number must be 11 digits long"))
        return mobile
                
    login_failure: Mapped[int] = mapped_column(server_default=text("'0'"))
    login_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    login_ip: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    token: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    status: Mapped[str] = mapped_column(StatusEnum, server_default=text("'normal'"))

    def __repr__(self):
        return f'<SysAdmin(id={self.id})>'

    @classmethod
    def from_dict(cls, data: dict) -> 'SysAdmin':
        valid_keys = {'login_failure', 'nickname', 'group_id', 'mobile', 'username', 'token', 'status', 'password', 'login_ip', 'avatar', 'id', 'login_at', 'email'}
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
    

    @property
    def password(self):
        '''密码属性（只读）'''
        return self._password
    
    @password.setter
    def password(self, pw: str):
        '''设置用户密码，并进行加密'''
        if not pw:
            raise ValueError(_("Password cannot be empty"))
        if len(pw) < 8:
            raise ValueError(_("Password must be at least 8 characters"))
        pw_hash = bcrypt.hashpw(pw.encode('utf8'), bcrypt.gensalt())
        self._password = pw_hash.decode('utf8')

    def check_password(self, pw: str) -> bool:
        '''校验用户密码'''
        if not pw:
            return False
        if len(pw) < 8:
            return False
        if self._password is not None:
            try:
                expected_hash = self._password.encode('utf8')
                return bcrypt.checkpw(pw.encode('utf8'), expected_hash)
            except ValueError:
                return False
        return False
