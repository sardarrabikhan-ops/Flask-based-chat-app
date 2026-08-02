# app/services/friends_service.py

from app.models import User, Friend
from app.services import BaseService

from app.schemas import ServiceResult
from app.constants import FriendStatus, UserStatus

from typing import Sequence


class FriendService(BaseService):
    """Provides friendships between users."""

    def get(self, user_id: int | None, friend_id: int | None) -> ServiceResult[Friend]:
        """Return the friendship for the given user ID and friend ID."""

        friendship_result = self._require_friendship(user_id, friend_id)

        if not friendship_result.success:
            return friendship_result

        assert friend_id is not None
        assert friendship_result.data is not None

        friendship = friendship_result.data

        return ServiceResult.ok(friendship)

    def get_friends(
        self, user_id: int | None, limit: int | None = None, offset: int | None = None
    ) -> ServiceResult[Sequence[User]]:
        """Return the friends for the given user ID."""

        user_result = self._require_user(user_id)

        if not user_result.success:
            assert user_result.errors is not None
            return ServiceResult.fail(user_result.errors)

        assert user_id is not None
        assert user_result.data is not None

        friendships = self.friend_repository.get_by_user_id(
            user_id, FriendStatus.ACTIVE, limit, offset, UserStatus.ACTIVE
        )

        friends: list[User] = []

        for friendship in friendships:
            friend = (
                friendship.friend if friendship.user_id == user_id else friendship.user
            )

            friends.append(friend)

        return ServiceResult.ok(friends)

    def delete(
        self, user_id: int | None, friend_id: int | None
    ) -> ServiceResult[Friend]:
        """Soft-delete a friend by marking its status as REMOVED."""

        friendship_result = self._require_friendship(user_id, friend_id)

        if not friendship_result.success:
            return friendship_result

        assert friendship_result.data is not None

        friendship = friendship_result.data

        friendship.status = FriendStatus.REMOVED

        return ServiceResult.ok(friendship)

    def are_friends(self, user_id: int | None, friend_id: int | None) -> bool:

        return self._require_friendship(user_id, friend_id).success
