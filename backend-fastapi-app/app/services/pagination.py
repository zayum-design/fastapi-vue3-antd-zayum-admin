"""
分页和过滤工具
提供标准化的分页和过滤功能
"""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    """分页参数"""

    page: int = Field(default=1, ge=1, description="页码")
    per_page: int = Field(default=10, ge=1, le=100, description="每页数量")

    @property
    def offset(self) -> int:
        """计算偏移量"""
        return (self.page - 1) * self.per_page


class SearchParams(PaginationParams):
    """搜索参数"""

    search: str | None = Field(default=None, description="搜索关键词")
    order_by: str | None = Field(default=None, description="排序字段，如 'created_at_desc'")


class FilterParams(BaseModel):
    """基础过滤参数"""

    pass


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应"""

    items: list[T]
    total: int
    page: int
    per_page: int
    total_pages: int

    @classmethod
    def create(cls, items: list[T], total: int, page: int, per_page: int) -> "PaginatedResponse[T]":
        """创建分页响应"""
        total_pages = (total + per_page - 1) // per_page if per_page > 0 else 0
        return cls(items=items, total=total, page=page, per_page=per_page, total_pages=total_pages)


class CursorPaginationParams(BaseModel):
    """游标分页参数"""

    cursor: str | None = Field(default=None, description="游标")
    limit: int = Field(default=20, ge=1, le=100, description="返回数量")


class CursorPaginatedResponse(BaseModel, Generic[T]):
    """游标分页响应"""

    items: list[T]
    next_cursor: str | None = None
    has_more: bool = False
