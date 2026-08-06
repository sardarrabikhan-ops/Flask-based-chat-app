# app/schemas/request_schemas/search_schema.py

from dataclasses import dataclass

from app.results import Result, ServiceResult


@dataclass(slots=True)
class SearchQuery:
    name: str | None = None


@dataclass(slots=True)
class SearchSchema:

    @classmethod
    def load(cls, args: dict[str, str]) -> Result[SearchQuery]:
        name = args.get("name")

        if name is None:
            return ServiceResult.ok(SearchQuery())

        name = " ".join(name.split())

        if not name:
            return ServiceResult.fail({"name": "Search term cannot be empty."})

        return ServiceResult.ok(SearchQuery(name=name))
