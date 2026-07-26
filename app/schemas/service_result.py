# app/schemas/service_result.py

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar, Generic

T = TypeVar("T")


@dataclass(slots=True)
class ServiceResult(Generic[T]):

    success: bool
    data: T | None = None
    errors: dict[str, str] | None = None

    @classmethod
    def ok(cls, data: T) -> ServiceResult[T]:
        return cls(True, data=data)

    @classmethod
    def fail(cls, errors: dict[str, str]) -> ServiceResult[T]:
        return cls(False, errors=errors)
