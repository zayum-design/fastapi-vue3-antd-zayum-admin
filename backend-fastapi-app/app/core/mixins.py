from datetime import UTC, datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column


class TimestampMixin:
    """Mixin 类，自动添加 `created_at` 和 `updated_at` 时间戳字段。"""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),  # 使用 lambda 避免默认值共享问题
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),  # 初始默认值
        onupdate=lambda: datetime.now(UTC),  # 更新时自动设置
    )
