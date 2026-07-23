# app/repositories/friends_repo.py

from sqlalchemy import select, or_
from sqlalchemy.orm import Session

from app.models import Friend
from app.constants import FriendStatus

from typing import Sequence


class FriendRepository:

    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, user_id: int, friend_id: int) -> Friend | None:
        statement = select(Friend).where(
            Friend.user_id == user_id, Friend.friend_id == friend_id
        )
        return self.session.scalar(statement)

    def get_active(self, user_id: int, friend_id: int) -> Friend | None:
        statement = select(Friend).where(
            Friend.user_id == user_id,
            Friend.friend_id == friend_id,
            Friend.status != FriendStatus.REMOVED.value,
        )
        return self.session.scalar(statement)

    def get_active_by_user_id(self, user_id: int) -> Sequence[Friend]:
        statement = select(Friend).where(
            or_(Friend.user_id == user_id, Friend.friend_id == user_id),
            Friend.status != FriendStatus.REMOVED.value,
        )
        return self.session.scalars(statement).all()

    def get_by_user_id(self, user_id: int) -> Sequence[Friend]:
        statement = select(Friend).where(
            or_(Friend.user_id == user_id, Friend.friend_id == user_id)
        )
        return self.session.scalars(statement).all()

    def create(self, friendship: Friend) -> Friend:
        self.session.add(friendship)
        return friendship
