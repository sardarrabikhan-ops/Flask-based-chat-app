# app/shemas/request_schemas/pagination_schema.py

from dataclasses import dataclass

from app.results import Result, ServiceResult


@dataclass(slots=True)
class Pagination:

    limit: int | None = None
    offset: int | None = None


@dataclass(slots=True)
class PaginationSchema:

    @classmethod
    def load(cls, args: dict) -> Result[Pagination]:

        errors: dict[str, str] = {}

        limit = args.get("limit")
        offset = args.get("offset")

        if limit is not None:
            try:
                limit = int(limit)

                if limit <= 0:
                    errors["limit"] = "Limit must be more than 0."

                if limit > 500:
                    errors["limit"] = "Limit must be less than 500."

            except (TypeError, ValueError):
                errors["limit"] = "Limit must be an integer."

        if offset is not None:
            try:
                offset = int(offset)

                if offset < 0:
                    errors["offset"] = "Offset must be more than or equal to 0."

            except (TypeError, ValueError):
                errors["offset"] = "Offset must be an integer."

        if errors:
            return ServiceResult.fail(errors)

        pagination = Pagination(
            limit=limit,
            offset=offset,
        )

        return ServiceResult.ok(pagination)
