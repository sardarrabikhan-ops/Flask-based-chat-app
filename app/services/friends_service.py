# app/services/friends_service.py

from app.models import User, Friend
from app.services import BaseService

from app.constants import FriendStatus, UserStatus
from app.results import ServiceResult, Result, FailureResult

from typing import Sequence


class FriendService(BaseService):
    """Provides friendships between users."""

    def get(self, user_id: int | None, friend_id: int | None) -> Result[Friend]:
        """Return the friendship for the given user ID and friend ID."""

        friendship_result = self._require_friendship(user_id, friend_id)

        if isinstance(friendship_result, FailureResult):
            return friendship_result

        friendship = friendship_result.data

        return ServiceResult.ok(friendship)

    def get_friends(
        self, user_id: int | None, limit: int | None = None, offset: int | None = None
    ) -> Result[Sequence[User]]:
        """Return the friends for the given user ID."""

        user_result = self._require_user(user_id)

        if isinstance(user_result, FailureResult):
            return user_result

        assert user_id is not None

        friendships = self.friend_repository.get_by_user_id(
            user_id, FriendStatus.ACTIVE, limit, offset, UserStatus.ACTIVE
        )

        friends: list[User] = [
            friendship.friend if friendship.user_id == user_id else friendship.user
            for friendship in friendships
        ]

        return ServiceResult.ok(friends)

    def delete(
        self, user_id: int | None, friend_id: int | None
    ) -> Result[Friend]:
        """Soft-delete a friend by marking its status as REMOVED."""

        friendship_result = self._require_friendship(user_id, friend_id)

        if isinstance(friendship_result, FailureResult):
            return friendship_result

        friendship = friendship_result.data

        friendship.status = FriendStatus.REMOVED

        return ServiceResult.ok(friendship)
