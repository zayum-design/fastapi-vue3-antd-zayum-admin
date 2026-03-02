"""
协议类定义（类似接口）
用于类型检查和抽象
"""

from datetime import datetime
from typing import Any, Protocol, TypeVar, runtime_checkable

T = TypeVar("T")


@runtime_checkable
class ModelProtocol(Protocol):
    """模型协议 - 所有 SQLAlchemy 模型应满足的接口"""

    id: int

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        ...

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ModelProtocol":
        """从字典创建"""
        ...


@runtime_checkable
class TimestampProtocol(Protocol):
    """时间戳协议 - 包含创建和更新时间"""

    created_at: datetime
    updated_at: datetime


@runtime_checkable
class SoftDeleteProtocol(Protocol):
    """软删除协议"""

    deleted_at: datetime | None
    is_deleted: bool

    def soft_delete(self) -> None:
        """执行软删除"""
        ...

    def restore(self) -> None:
        """恢复软删除"""
        ...


@runtime_checkable
class CRUDProtocol(Protocol[T]):
    """CRUD 协议 - 标准 CRUD 操作接口"""

    def get(self, id: Any) -> T | None:
        """获取单条"""
        ...

    def get_multi(self, *, page: int = 1, per_page: int = 20) -> list[T]:
        """获取多条"""
        ...

    def create(self, obj_in: Any) -> T:
        """创建"""
        ...

    def update(self, id: Any, obj_in: Any) -> T | None:
        """更新"""
        ...

    def delete(self, id: Any) -> bool:
        """删除"""
        ...


@runtime_checkable
class RepositoryProtocol(Protocol[T]):
    """Repository 协议 - 数据访问层接口"""

    def get_by_id(self, id: Any) -> T | None:
        """通过 ID 获取"""
        ...

    def get_by_ids(self, ids: list[Any]) -> list[T]:
        """通过 IDs 批量获取"""
        ...

    def find_one(self, **filters) -> T | None:
        """条件查询单条"""
        ...

    def find_all(self, **filters) -> list[T]:
        """条件查询多条"""
        ...

    def exists(self, **filters) -> bool:
        """检查是否存在"""
        ...

    def count(self, **filters) -> int:
        """计数"""
        ...

    def save(self, obj: T) -> T:
        """保存"""
        ...

    def save_all(self, objs: list[T]) -> list[T]:
        """批量保存"""
        ...

    def delete_by_id(self, id: Any) -> bool:
        """通过 ID 删除"""
        ...

    def delete_by_ids(self, ids: list[Any]) -> int:
        """通过 IDs 批量删除"""
        ...


@runtime_checkable
class CacheProtocol(Protocol):
    """缓存协议"""

    def get(self, key: str) -> Any | None:
        """获取缓存"""
        ...

    def set(self, key: str, value: Any, expire: int | None = None) -> bool:
        """设置缓存"""
        ...

    def delete(self, key: str) -> bool:
        """删除缓存"""
        ...

    def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        ...

    def clear(self) -> bool:
        """清空缓存"""
        ...


@runtime_checkable
class LoggerProtocol(Protocol):
    """日志协议"""

    def debug(self, msg: str, *args, **kwargs) -> None:
        """调试日志"""
        ...

    def info(self, msg: str, *args, **kwargs) -> None:
        """信息日志"""
        ...

    def warning(self, msg: str, *args, **kwargs) -> None:
        """警告日志"""
        ...

    def error(self, msg: str, *args, **kwargs) -> None:
        """错误日志"""
        ...

    def critical(self, msg: str, *args, **kwargs) -> None:
        """严重错误日志"""
        ...
