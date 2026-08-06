# app/schemas/response_builder.py

from app.results import Result, FailureResult
from app.schemas import BaseSchema

from typing import Sequence, TypeVar, Any

T = TypeVar("T")


class ResponseBuilder:

    _schema = BaseSchema()

    @classmethod
    def build(
        cls,
        result: Result,
        *,
        include: set[str] | None = None,
        exclude: set[str] | None = None
    ) -> tuple[dict[str, Any], int]:

        if isinstance(result, FailureResult):

            return (
                {
                    "success": False,
                    "code": result.code.code,
                    "errors": result.errors,
                },
                result.code.http_status,
            )

        return (
            {
                "success": True,
                "code": result.code.code,
                "data": cls._serialize(result.data, include=include, exclude=exclude),
            },
            result.code.http_status,
        )

    @classmethod
    def _serialize(
        cls,
        data: Any,
        *,
        include: set[str] | None = None,
        exclude: set[str] | None = None
    ) -> Any:

        if data is None:
            return None

        if isinstance(data, Sequence) and not isinstance(data, (str, bytes, bytearray)):
            return cls._schema.dump_many(data, include=include, exclude=exclude)

        if cls._schema.can_dump(data):
            return cls._schema.dump(data, include=include, exclude=exclude)

        return data
