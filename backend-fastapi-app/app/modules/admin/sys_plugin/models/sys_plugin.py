from sqlalchemy import DECIMAL, SMALLINT, Enum, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.mixins import TimestampMixin
from app.core.models import Base

# ENUM definitions
StatusEnum = Enum("normal", "hidden", name="status_enum", create_constraint=True)


class SysPlugin(TimestampMixin, Base):
    __tablename__ = "sys_plugin"
    __table_args__ = ()

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(120))
    author: Mapped[str] = mapped_column(String(80))
    uuid: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(String(255))
    version: Mapped[str] = mapped_column(String(50))
    downloads: Mapped[int] = mapped_column()
    download_url: Mapped[str] = mapped_column(String(255))
    md5_hash: Mapped[str] = mapped_column(String(32))
    price: Mapped[float | None] = mapped_column(DECIMAL(10, 2), server_default=text("'0.00'"))
    paid: Mapped[int] = mapped_column(SMALLINT)
    installed: Mapped[int] = mapped_column(SMALLINT)
    enabled: Mapped[int] = mapped_column(SMALLINT)
    setting_menu: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(StatusEnum)

    def __repr__(self):
        return f"<SysPlugin(id={self.id})>"

    @classmethod
    def from_dict(cls, data: dict) -> "SysPlugin":
        valid_keys = {
            "setting_menu",
            "downloads",
            "status",
            "version",
            "id",
            "paid",
            "author",
            "md5_hash",
            "title",
            "installed",
            "uuid",
            "price",
            "description",
            "download_url",
            "enabled",
        }
        filtered_data = {key: value for key, value in data.items() if key in valid_keys}
        return cls(**filtered_data)

    def to_dict(self) -> dict:
        result_dict = {}
        for column in self.__table__.columns:
            if column.key == "password":
                continue
            value = getattr(self, column.key, None)
            result_dict[column.key] = value
        return result_dict
