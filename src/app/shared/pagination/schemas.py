from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


class PageMetadata(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int


class Page(BaseModel, Generic[T]):
    items: list[T]
    metadata: PageMetadata

    @classmethod
    def build(
        cls,
        items: list[T],
        *,
        page: int,
        page_size: int,
        total_items: int,
    ) -> "Page[T]":
        total_pages = (total_items + page_size - 1) // page_size
        return cls(
            items=items,
            metadata=PageMetadata(
                page=page,
                page_size=page_size,
                total_items=total_items,
                total_pages=total_pages,
            ),
        )
