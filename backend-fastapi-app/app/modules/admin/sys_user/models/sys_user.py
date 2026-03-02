import logging
import re
from datetime import date, datetime

import bcrypt
from fastapi_babel import _
from sqlalchemy import DATE, DATETIME, DECIMAL, SMALLINT, Enum, String, text
from sqlalchemy.orm import Mapped, mapped_column, validates

from app.core.mixins import TimestampMixin
from app.core.models import Base

logger = logging.getLogger(__name__)

# ENUM definitions
GenderEnum = Enum("male", "female", name="gender_enum", create_constraint=True)
StatusEnum = Enum("normal", "hidden", "delete", name="status_enum", create_constraint=True)
PlatformEnum = Enum(
    "ios", "mac", "android", "web", "pc", "other", name="platform_enum", create_constraint=True
)


class SysUser(TimestampMixin, Base):
    __tablename__ = "sys_user"
    __table_args__ = ()

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_group_id: Mapped[int] = mapped_column(server_default=text("'1'"))
    username: Mapped[str] = mapped_column(String(32))

    @validates("username")
    def validate_username(self, key, username):
        if not username:
            raise ValueError(_("Username is required"))
        if not username.isalnum():
            logger.error("Username contains non-alphanumeric characters: {username}")
            raise ValueError(_("Username must be alphanumeric"))
        if len(username) > 32:
            logger.error("Username too long: {username} (max 32 chars)")
            raise ValueError(_("Username too long (max 32 characters)"))
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

    _password: Mapped[str | None] = mapped_column("password", String(120), nullable=True)

    @validates("_password")
    def validate__password_length(self, key, value):
        if not value:
            raise ValueError(_("Value is required"))
        if len(value) > 120:
            logger.error("Value too long for {key}: {value} (max 120 chars)")
            raise ValueError(_("Value too long (max 120 characters)"))
        return value

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

    mobile: Mapped[str] = mapped_column(String(16))

    @validates("mobile")
    def validate_mobile_length(self, key, value):
        if not value:
            raise ValueError(_("Value is required"))
        if len(value) > 16:
            logger.error("Value too long for {key}: {value} (max 16 chars)")
            raise ValueError(_("Value too long (max 16 characters)"))
        return value

    avatar: Mapped[str | None] = mapped_column(String(255), nullable=True)
    level: Mapped[int] = mapped_column(SMALLINT, server_default=text("'0'"))
    gender: Mapped[str] = mapped_column(GenderEnum, server_default=text("'male'"))
    birthday: Mapped[date | None] = mapped_column(DATE, nullable=True)
    bio: Mapped[str | None] = mapped_column(String(100), server_default=text("'No  Data'"))
    balance: Mapped[float | None] = mapped_column(DECIMAL(10, 2), server_default=text("'0.00'"))
    score: Mapped[int] = mapped_column(server_default=text("'0'"))
    successions: Mapped[int] = mapped_column(server_default=text("'0'"))
    max_successions: Mapped[int] = mapped_column(server_default=text("'0'"))
    prev_time: Mapped[datetime | None] = mapped_column(
        DATETIME, server_default=text("CURRENT_TIMESTAMP")
    )
    login_time: Mapped[datetime | None] = mapped_column(
        DATETIME, server_default=text("CURRENT_TIMESTAMP")
    )
    login_ip: Mapped[str | None] = mapped_column(String(50), nullable=True)
    login_failure: Mapped[int] = mapped_column(SMALLINT, server_default=text("'0'"))
    join_ip: Mapped[str | None] = mapped_column(String(50), nullable=True)
    verification: Mapped[str | None] = mapped_column(String(255), nullable=True)
    token: Mapped[str | None] = mapped_column(String(250), nullable=True)
    status: Mapped[str] = mapped_column(StatusEnum, server_default=text("'normal'"))
    platform: Mapped[str] = mapped_column(PlatformEnum, server_default=text("'other'"))

    def __repr__(self):
        return f"<SysUser(id={self.id})>"

    @classmethod
    def from_dict(cls, data: dict) -> "SysUser":
        valid_keys = {
            "verification",
            "login_failure",
            "score",
            "user_group_id",
            "level",
            "login_ip",
            "gender",
            "status",
            "nickname",
            "prev_time",
            "balance",
            "id",
            "password",
            "max_successions",
            "login_time",
            "token",
            "username",
            "successions",
            "birthday",
            "join_ip",
            "avatar",
            "mobile",
            "bio",
            "email",
            "platform",
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
        # 如果密码为空字符串，则不更新密码（保持原密码不变）
        if pw == "":
            return
        if not pw:
            raise ValueError(_("Password cannot be empty"))
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
        if self._password:
            try:
                expected_hash = self._password.encode("utf8")
                return bcrypt.checkpw(pw.encode("utf8"), expected_hash)
            except ValueError:
                return False
        return False
