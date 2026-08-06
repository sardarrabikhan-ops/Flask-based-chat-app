# app/schemas/base_schema.py

from __future__ import annotations

from app.models import User

from datetime import datetime
from enum import Enum
from typing import Sequence, Any

from sqlalchemy import inspect
from sqlalchemy.exc import NoInspectionAvailable


class BaseSchema:

    _MODEL_EXCLUDES: dict[type[Any], set[str]] = {
        User: {
            "password",
            "failed_attempts",
            "lock_until",
        },
    }

    def dump(
        self,
        obj: Any,
        *,
        include: set[str] | None = None,
        exclude: set[str] | None = None,
    ) -> dict[str, Any]:

        exclude = (exclude or set()) | self._MODEL_EXCLUDES.get(type(obj), set())
        include = include or set()

        data: dict[str, Any] = {}

        mapper = inspect(obj)

        for column in mapper.mapper.column_attrs:

            key = column.key

            if include and key not in include:
                continue

            if key in exclude:
                continue

            value = getattr(obj, key)

            if isinstance(value, Enum):
                value = value.value

            elif isinstance(value, datetime):
                value = value.isoformat()

            data[key] = value

        return data

    @staticmethod
    def can_dump(obj: Any) -> bool:
        try:
            inspect(obj)
            return True
        except NoInspectionAvailable:
            return False

    def dump_many(
        self,
        objects: Sequence[Any],
        *,
        exclude: set[str] | None = None,
        include: set[str] | None = None,
    ) -> list[dict[str, Any]]:

        return [self.dump(obj, include=include, exclude=exclude) for obj in objects]
