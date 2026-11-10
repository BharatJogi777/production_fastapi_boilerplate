from typing import Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")

class ResponseEnvelope(BaseModel, Generic[T]):
    data: T
    message: str | None = None
    meta: dict[str, object] = Field(default_factory=dict)
