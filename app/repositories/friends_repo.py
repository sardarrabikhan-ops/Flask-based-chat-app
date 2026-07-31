# app/repositories/friends_repo.py

from sqlalchemy import select, or_
from sqlalchemy.orm import Session

from app.models import Friend
from app.constants import FriendStatus

from typing import Sequence


class FriendRepository:

    def __init__(self, session: Session) -> None:
        self.session = session

    def get(
        self,
        user_id: int,
        friend_id: int,
    ) -> Friend | None:

        user_id, friend_id = sorted([user_id, friend_id])

        statement = select(Friend).where(
            Friend.user_id == user_id, Friend.friend_id == friend_id
        )
        return self.session.scalar(statement)

    def get_by_user_id(
        self,
        user_id: int,
        status: FriendStatus | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Sequence[Friend]:

        statement = select(Friend).where(
            or_(Friend.user_id == user_id, Friend.friend_id == user_id)
        )

        if status is not None:
            statement = statement.where(Friend.status == status)

        if limit is not None:
            statement = statement.limit(limit)

        if offset is not None:
            statement = statement.offset(offset)

        statement = statement.order_by(Friend.created_at.desc())

        return self.session.scalars(statement).all()

    def exists(self, user_id: int, friend_id: int) -> bool:

        user_id, friend_id = sorted([user_id, friend_id])

        statement = select(Friend).where(
            Friend.user_id == user_id,
            Friend.friend_id == friend_id,
            Friend.status == FriendStatus.ACTIVE,
        )
        return self.session.scalar(statement) is not None

    def create(self, friendship: Friend) -> Friend:
        self.session.add(friendship)
        return friendship
