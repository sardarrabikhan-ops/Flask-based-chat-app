# tests/schemas/test_pagination_schema.py

from app.results import FailureResult
from app.schemas.request_schemas.pagination_schema import PaginationSchema


def test_pagination_rejects_limit_over_maximum():
    result = PaginationSchema.load({"limit": "501"})

    assert isinstance(result, FailureResult)
