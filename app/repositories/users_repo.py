# app/repositories/users_repo.py

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User
from app.constants import UserStatus

from typing import Sequence


class UserRepository:

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, user_id: int) -> User | None:
        return self.session.get(User, user_id)

    def get_all(
        self,
        status: UserStatus | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Sequence[User]:
        statement = select(User)

        if status is not None:
            statement = statement.where(User.status == status)

        if offset is not None:
            statement = statement.offset(offset)

        if limit is not None:
            statement = statement.limit(limit)

        return self.session.scalars(statement).all()

    def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        return self.session.scalar(statement)

    def get_by_phone_number(self, phone_number: str) -> User | None:
        statement = select(User).where(User.phone_number == phone_number)
        return self.session.scalar(statement)

    def exists_by_email(self, email: str) -> bool:
        statement = select(User).where(User.email == email)
        return self.session.scalar(statement) is not None

    def exists_by_phone_number(self, phone_number: str) -> bool:
        statement = select(User).where(User.phone_number == phone_number)
        return self.session.scalar(statement) is not None

    def exists_by_phone_number_except_user(
        self, user_id: int, phone_number: str
    ) -> bool:
        statement = select(User).where(
            User.phone_number == phone_number, User.id != user_id
        )
        return self.session.scalar(statement) is not None

    def create(self, user: User) -> User:
        self.session.add(user)
        return user
