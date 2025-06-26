from typing import Literal, Optional
from datetime import date, datetime
from sqlalchemy import String, Integer, JSON, text, Enum, DATETIME
from sqlalchemy.orm import Mapped, mapped_column
from .mixins import TimestampMixin
from app.models import Base

# ENUM definitions
Rule_typeEnum = Enum('menu', 'action', name="rule_type_enum", create_constraint=True)
Menu_display_typeEnum = Enum('ajax', 'addtabs', 'blank', 'dialog', name="menu_display_type_enum", create_constraint=True)
StatusEnum = Enum('normal', 'hidden', 'deleted', name="status_enum", create_constraint=True)

class SysAdminRule(TimestampMixin, Base):
    __tablename__ = 'sys_admin_rule'
    __table_args__ = ()

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    rule_type: Mapped[str] = mapped_column(Rule_typeEnum, server_default=text("'menu'"))
    parent_id: Mapped[Optional[int]] = mapped_column(nullable=True)
    name: Mapped[str] = mapped_column(String(150))
    path: Mapped[str] = mapped_column(String(50))
    component: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    redirect: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    meta: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    permission: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    menu_display_type: Mapped[Optional[str]] = mapped_column(Menu_display_typeEnum, server_default=text("'addtabs'"))
    model_name: Mapped[str] = mapped_column(String(80))
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DATETIME, nullable=True)
    weigh: Mapped[int] = mapped_column(server_default=text("'0'"))
    status: Mapped[str] = mapped_column(StatusEnum, server_default=text("'normal'"))

    def __repr__(self):
        return f'<SysAdminRule(id={self.id})>'

    @classmethod
    def from_dict(cls, data: dict) -> 'SysAdminRule':
        valid_keys = {'permission', 'status', 'name', 'rule_type', 'weigh', 'path', 'redirect', 'parent_id', 'model_name', 'meta', 'component', 'deleted_at', 'id', 'menu_display_type'}
        filtered_data = {key: value for key, value in data.items() if key in valid_keys}
        return cls(**filtered_data)
    


    def to_dict(self) -> dict:
        result_dict = {}
        for column in self.__table__.columns:
            if column.key == 'password':
                continue
            value = getattr(self, column.key, None)
            result_dict[column.key] = value
        return result_dict
