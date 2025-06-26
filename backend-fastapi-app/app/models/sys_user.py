import re
import logging
import bcrypt
from typing import Literal, Optional
from datetime import date, datetime
from sqlalchemy import String, Integer, SMALLINT, DECIMAL, DATE, DATETIME, text, Enum
from sqlalchemy.orm import validates, Mapped, mapped_column
from .mixins import TimestampMixin
from app.models import Base
from fastapi_babel import _

logger = logging.getLogger(__name__)

# ENUM definitions
GenderEnum = Enum('male', 'female', name="gender_enum", create_constraint=True)
StatusEnum = Enum('normal', 'hidden', 'delete', name="status_enum", create_constraint=True)

class SysUser(TimestampMixin, Base):
    __tablename__ = 'sys_user'
    __table_args__ = ()

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_group_id: Mapped[int] = mapped_column(server_default=text("'1'"))
    username: Mapped[str] = mapped_column(String(32))

    @validates("username")
    def validate_username(self, key, username):
        if not username:
            raise ValueError(_("Username is required"))
        if not username.isalnum():
            logger.error(f"Username contains non-alphanumeric characters: {username}")
            raise ValueError(_("Username must be alphanumeric"))
        if len(username) > 32:
            logger.error(f"Username too long: {username} (max 32 chars)")
            raise ValueError(_(f"Username too long (max 32 characters)"))
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
                
    _password: Mapped[Optional[str]] = mapped_column('password', String(120), nullable=True)

    @validates("_password")
    def validate__password_length(self, key, value):
        if not value:
            raise ValueError(_("Value is required"))
        if len(value) > 120:
            logger.error(f"Value too long for {key}: {value} (max 120 chars)")
            raise ValueError(_(f"Value too long (max 120 characters)"))
        return value
                    
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
                
    mobile: Mapped[str] = mapped_column(String(16))

    @validates("mobile")
    def validate_mobile_length(self, key, value):
        if not value:
            raise ValueError(_("Value is required"))
        if len(value) > 16:
            logger.error(f"Value too long for {key}: {value} (max 16 chars)")
            raise ValueError(_(f"Value too long (max 16 characters)"))
        return value
                    
    avatar: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    level: Mapped[int] = mapped_column(SMALLINT, server_default=text("'0'"))
    gender: Mapped[str] = mapped_column(GenderEnum, server_default=text("'male'"))
    birthday: Mapped[Optional[date]] = mapped_column(DATE, nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(String(100), server_default=text("'No  Data'"))
    balance: Mapped[Optional[float]] = mapped_column(DECIMAL(10, 2), server_default=text("'0.00'"))
    score: Mapped[int] = mapped_column(server_default=text("'0'"))
    successions: Mapped[int] = mapped_column(server_default=text("'0'"))
    max_successions: Mapped[int] = mapped_column(server_default=text("'0'"))
    prev_time: Mapped[Optional[datetime]] = mapped_column(DATETIME, server_default=text('CURRENT_TIMESTAMP'))
    login_time: Mapped[Optional[datetime]] = mapped_column(DATETIME, server_default=text('CURRENT_TIMESTAMP'))
    login_ip: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    login_failure: Mapped[int] = mapped_column(SMALLINT, server_default=text("'0'"))
    join_ip: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    verification: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    token: Mapped[Optional[str]] = mapped_column(String(250), nullable=True)
    status: Mapped[str] = mapped_column(StatusEnum, server_default=text("'normal'"))

    def __repr__(self):
        return f'<SysUser(id={self.id})>'

    @classmethod
    def from_dict(cls, data: dict) -> 'SysUser':
        valid_keys = {'verification', 'login_failure', 'score', 'user_group_id', 'level', 'login_ip', 'gender', 'status', 'nickname', 'prev_time', 'balance', 'id', 'password', 'max_successions', 'login_time', 'token', 'username', 'successions', 'birthday', 'join_ip', 'avatar', 'mobile', 'bio', 'email'}
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
        if self._password:
            try:
                expected_hash = self._password.encode('utf8')
                return bcrypt.checkpw(pw.encode('utf8'), expected_hash)
            except ValueError:
                return False
        return False
