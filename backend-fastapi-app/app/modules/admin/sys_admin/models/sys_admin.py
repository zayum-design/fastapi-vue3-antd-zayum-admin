import logging
import re
from datetime import datetime

import bcrypt
from fastapi_babel import _
from sqlalchemy import Enum, String, text
from sqlalchemy.orm import Mapped, mapped_column, validates

from app.core.mixins import TimestampMixin
from app.core.models import Base

logger = logging.getLogger(__name__)

# ENUM definitions
StatusEnum = Enum("normal", "hidden", name="status_enum", create_constraint=True)


class SysAdmin(TimestampMixin, Base):
    __tablename__ = "sys_admin"
    __table_args__ = ()

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(server_default=text("'1'"))
    username: Mapped[str] = mapped_column(String(20))

    @validates("username")
    def validate_username(self, key, username):
        if not username:
            raise ValueError(_("Username is required"))
        if not username.isalnum():
            logger.error("Username contains non-alphanumeric characters: {username}")
            raise ValueError(_("Username must be alphanumeric"))
        if len(username) > 20:
            logger.error("Username too long: {username} (max 20 chars)")
            raise ValueError(_("Username too long (max 20 characters)"))
        return username

    nickname: Mapped[str] = mapped_column(String(50))

    @validates("nickname")
    def validate_nickname(self, key, name):
        if not name:
            raise ValueError(_("Name is required"))
        if not re.match(r"^[\w\s\-\.]+$", name):
            logger.error("Invalid characters in name: {name}")
            raise ValueError(_("Name contains invalid characters"))
        if len(name) > 50:
            logger.error("Name too long: {name} (max 50 chars)")
            raise ValueError(_("Name too long (max 50 characters)"))
        return name

    _password: Mapped[str | None] = mapped_column("password", String(128), nullable=True)

    @validates("_password")
    def validate__password_length(self, key, value):
        if not value:
            raise ValueError(_("Value is required"))
        if len(value) > 128:
            logger.error("Value too long for {key}: {value} (max 128 chars)")
            raise ValueError(_("Value too long (max 128 characters)"))
        return value

    avatar: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email: Mapped[str] = mapped_column(String(100))

    @validates("email")
    def validate_email(self, key, address):
        if not address:
            raise ValueError(_("Email is required"))
        if "@" not in address:
            logger.error("Invalid email address provided: {address}")
            raise ValueError(_("Invalid email address"))
        if len(address) > 100:
            logger.error("Email too long: {address} (max 100 chars)")
            raise ValueError(_("Email too long (max 100 characters)"))
        return address

    mobile: Mapped[str] = mapped_column(String(11))

    @validates("mobile")
    def validate_mobile(self, key, mobile):
        if not mobile:
            raise ValueError(_("Mobile number is required"))
        if not mobile.isdigit():
            logger.error("Mobile number contains non-digit characters: {mobile}")
            raise ValueError(_("Mobile number must contain only digits"))
        if len(mobile) != 11:
            logger.error("Mobile number length is not 11 digits: {mobile}")
            raise ValueError(_("Mobile number must be 11 digits long"))
        return mobile

    login_failure: Mapped[int] = mapped_column(server_default=text("'0'"))
    login_at: Mapped[datetime | None] = mapped_column(nullable=True)
    login_ip: Mapped[str | None] = mapped_column(String(50), nullable=True)
    token: Mapped[str | None] = mapped_column(String(512), nullable=True)
    status: Mapped[str] = mapped_column(StatusEnum, server_default=text("'normal'"))

    def __repr__(self):
        return f"<SysAdmin(id={self.id})>"

    @classmethod
    def from_dict(cls, data: dict) -> "SysAdmin":
        valid_keys = {
            "login_failure",
            "nickname",
            "group_id",
            "mobile",
            "username",
            "token",
            "status",
            "password",
            "login_ip",
            "avatar",
            "id",
            "login_at",
            "email",
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

    @property
    def password(self):
        """密码属性（只读）"""
        return self._password

    @password.setter
    def password(self, pw: str):
        """设置用户密码，并进行加密"""
        # 如果密码为空，则不设置密码（保持原密码不变）
        if not pw:
            return
        if len(pw) < 8:
            raise ValueError(_("Password must be at least 8 characters"))
        pw_hash = bcrypt.hashpw(pw.encode("utf8"), bcrypt.gensalt())
        self._password = pw_hash.decode("utf8")

    def check_password(self, pw: str) -> bool:
        """校验用户密码"""
        if not pw:
            return False
        if len(pw) < 8:
            return False
        if self._password is not None:
            try:
                expected_hash = self._password.encode("utf8")
                return bcrypt.checkpw(pw.encode("utf8"), expected_hash)
            except ValueError:
                return False
        return False
