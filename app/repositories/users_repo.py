# app/repositories/users_repo.py

from sqlalchemy import select, func, case
from sqlalchemy.sql import ColumnElement

from app.repositories import BaseRepository
from app.models import User

from app.constants import UserStatus
from app.utils import escape_like

from typing import Sequence


class UserRepository(BaseRepository):

    def get_by_id(self, user_id: int) -> User | None:
        return self.session.get(User, user_id)

    def get_by_ids(
        self,
        ids: list[int],
        limit: int | None = None,
        offset: int | None = None,
    ) -> Sequence[User]:

        statement = select(User).where(
            User.id.in_(ids), User.status != UserStatus.DELETED
        )

        statement = self._paginate(statement, limit, offset)

        return self.session.scalars(statement).all()

    def get_all(
        self,
        status: UserStatus | None = None,
        limit: int | None = None,
        offset: int | None = None,
        order_by: ColumnElement | None = None,
    ) -> Sequence[User]:
        statement = select(User)

        if status is not None:
            statement = statement.where(User.status == status)

        statement = self._paginate(statement, limit, offset, order_by)

        return self.session.scalars(statement).all()

    def search_by_name(
        self,
        name: str,
        status: UserStatus | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Sequence[User]:

        name = escape_like(name)

        exact = name
        starts = f"{name}%"
        contains = f"%{name}%"

        full_name = func.concat(User.firstname, " ", User.lastname)

        rank = case(
            (full_name.ilike(exact, escape="\\"), 0),
            (full_name.ilike(starts, escape="\\"), 1),
            (full_name.ilike(contains, escape="\\"), 2),
            else_=3,
        )

        statement = (
            select(User)
            .where(full_name.ilike(contains, escape="\\"))
            .order_by(rank, User.firstname, User.lastname, User.id)
        )

        if status is not None:
            statement = statement.where(User.status == status)

        statement = self._paginate(statement, limit, offset)

        return self.session.scalars(statement).all()

    def get_by_email(self, email: str, deleted: bool = False) -> User | None:
        statement = select(User).where(User.email == email)

        if not deleted:
            statement = statement.where(User.status != UserStatus.DELETED)

        return self.session.scalar(statement)

    def get_by_phone_number(self, phone_number: str) -> User | None:
        statement = select(User).where(
            User.phone_number == phone_number, User.status != UserStatus.DELETED
        )
        return self.session.scalar(statement)

    def exists_by_email(self, email: str) -> bool:
        statement = select(User).where(
            User.email == email, User.status != UserStatus.DELETED
        )

        return self.session.scalar(statement) is not None

    def exists_by_phone_number(self, phone_number: str) -> bool:
        statement = select(User).where(
            User.phone_number == phone_number, User.status != UserStatus.DELETED
        )
        return self.session.scalar(statement) is not None

    def exists_by_phone_number_except_user(
        self, user_id: int, phone_number: str
    ) -> bool:
        statement = select(User).where(
            User.phone_number == phone_number,
            User.id != user_id,
            User.status != UserStatus.DELETED,
        )
        return self.session.scalar(statement) is not None

    def create(self, user: User) -> User:
        self.session.add(user)
        return user
