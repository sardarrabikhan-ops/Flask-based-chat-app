# app/repositories/friends_repo.py

from sqlalchemy import select, or_
from sqlalchemy.orm import aliased, selectinload

from app.repositories import BaseRepository
from app.models import Friend, User
from app.constants import FriendStatus, UserStatus

from typing import Sequence


class FriendRepository(BaseRepository):

    def get(
        self,
        user_id: int,
        friend_id: int,
    ) -> Friend | None:

        user_id, friend_id = sorted((user_id, friend_id))

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
        member_status: UserStatus | None = None,
    ) -> Sequence[Friend]:

        user = aliased(User)
        friend = aliased(User)

        statement = (
            select(Friend)
            .options(
                selectinload(Friend.user),
                selectinload(Friend.friend),
            )
            .join(user, Friend.user)
            .join(friend, Friend.friend)
            .where(
                or_(
                    Friend.user_id == user_id,
                    Friend.friend_id == user_id,
                ),
            )
        )

        if status is not None:
            statement = statement.where(Friend.status == status)

        if member_status is not None:
            statement = statement.where(
                user.status == member_status,
                friend.status == member_status,
            )

        statement = self._paginate(statement, limit, offset, Friend.created_at.desc())

        return self.session.scalars(statement).all()

    def exists(self, user_id: int, friend_id: int, deleted: bool = False) -> bool:

        user_id, friend_id = sorted((user_id, friend_id))

        statement = select(Friend).where(
            Friend.user_id == user_id,
            Friend.friend_id == friend_id,
        )

        if not deleted:
            statement = statement.where(Friend.status != FriendStatus.REMOVED)

        return self.session.scalar(statement) is not None

    def create(self, friendship: Friend) -> Friend:
        self.session.add(friendship)
        return friendship
