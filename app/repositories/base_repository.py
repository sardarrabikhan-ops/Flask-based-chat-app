# app/repositories/base_repository.py

from sqlalchemy import Select
from sqlalchemy.orm import Session
from sqlalchemy.sql import ColumnElement

from typing import Any


class BaseRepository:

    def __init__(self, session: Session) -> None:
        self.session = session

    @staticmethod
    def _paginate(
        statement: Select[Any],
        limit: int | None,
        offset: int | None,
        order_by: ColumnElement | None = None,
    ) -> Select[Any]:

        if limit is not None:
            statement = statement.limit(limit)

        if offset is not None:
            statement = statement.offset(offset)

        if order_by is not None:
            statement = statement.order_by(order_by)

        return statement
