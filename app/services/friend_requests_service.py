# app/services/friend_requests_service.py

from app.models import FriendRequest
from app.services import BaseService

from app.schemas import ServiceResult
from app.constants import FriendRequestStatus

from typing import Sequence


class FriendRequestService(BaseService):
    """Provides friend-request-related business logic."""

    def send(
        self, sender_id: int | None, receiver_id: int | None
    ) -> ServiceResult[FriendRequest]:
        """Send a friend request to receiver."""

        if sender_id == receiver_id:
            return ServiceResult.fail(
                {"friend_request": "You cannot send a friend request to yourself."}
            )

        sender_result = self._require_user(sender_id)

        if not sender_result.success:
            assert sender_result.errors is not None
            return ServiceResult.fail(sender_result.errors)

        assert sender_id is not None

        receiver_result = self._require_receiver(receiver_id)

        if not receiver_result.success:
            assert receiver_result.errors is not None
            return ServiceResult.fail(receiver_result.errors)

        assert receiver_id is not None

        is_friend = self.friend_repository.exists(sender_id, receiver_id)

        if is_friend:
            return ServiceResult.fail({"friendship": "Friendship already exists."})

        is_request = self.friend_request_repository.exists(
            sender_id, receiver_id, FriendRequestStatus.PENDING
        )
        is_reverse_request = self.friend_request_repository.exists(
            receiver_id, sender_id, FriendRequestStatus.PENDING
        )

        if is_request or is_reverse_request:
            return ServiceResult.fail(
                {"friend_request": "A pending friend request already exist."}
            )

        friend_request = FriendRequest(sender_id=sender_id, receiver_id=receiver_id)
        friend_request = self.friend_request_repository.create(friend_request)

        return ServiceResult.ok(friend_request)

    def accept(
        self, sender_id: int | None, receiver_id: int | None
    ) -> ServiceResult[FriendRequest]:
        """Accept the friend request by marking it's status as ACCEPTED."""

        result = self._change_friend_request_status(
            sender_id, receiver_id, FriendRequestStatus.ACCEPTED
        )

        if not result.success:
            assert result.errors is not None
            return ServiceResult.fail(result.errors)

        assert sender_id is not None
        assert receiver_id is not None
        assert result.data is not None

        friend_request = result.data

        self._create_friendship(sender_id, receiver_id)

        return ServiceResult.ok(friend_request)

    def reject(
        self, sender_id: int | None, receiver_id: int | None
    ) -> ServiceResult[FriendRequest]:
        """Reject the friend request by marking it's status as REJECTED."""

        result = self._change_friend_request_status(
            sender_id, receiver_id, FriendRequestStatus.REJECTED
        )

        if not result.success:
            assert result.errors is not None
            return ServiceResult.fail(result.errors)

        assert result.data is not None

        friend_request = result.data

        return ServiceResult.ok(friend_request)

    def cancel(
        self, sender_id: int | None, receiver_id: int | None
    ) -> ServiceResult[FriendRequest]:
        """Cancel the friend request by marking it's status as CANCELED."""

        result = self._change_friend_request_status(
            sender_id, receiver_id, FriendRequestStatus.CANCELED
        )

        if not result.success:
            assert result.errors is not None
            return ServiceResult.fail(result.errors)

        assert result.data is not None

        friend_request = result.data

        return ServiceResult.ok(friend_request)

    def get(
        self,
        sender_id: int | None,
        receiver_id: int | None,
        status: FriendRequestStatus = FriendRequestStatus.PENDING,
    ) -> ServiceResult[Sequence[FriendRequest]]:
        """Return all the friend request belongs to the sender_id user and receiver_id user. By default it returns the pending requests."""

        sender_result = self._require_user(sender_id)

        if not sender_result.success:
            assert sender_result.errors is not None
            return ServiceResult.fail(sender_result.errors)

        assert sender_id is not None

        receiver_result = self._require_receiver(receiver_id)

        if not receiver_result.success:
            assert receiver_result.errors is not None
            return ServiceResult.fail(receiver_result.errors)

        assert receiver_id is not None

        friend_requests = self.friend_request_repository.get(
            sender_id, receiver_id, status
        )

        return ServiceResult.ok(friend_requests)

    def get_sent_requests(
        self,
        sender_id: int | None,
        status: FriendRequestStatus = FriendRequestStatus.PENDING,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ServiceResult[Sequence[FriendRequest]]:
        """Return all friend requests sent by the given user. By default it returns the pending requests."""

        sender_result = self._require_user(sender_id)

        if not sender_result.success:
            assert sender_result.errors is not None
            return ServiceResult.fail(sender_result.errors)

        assert sender_id is not None

        friend_requests = self.friend_request_repository.get_by_sender_id(
            sender_id, status=status, limit=limit, offset=offset
        )

        return ServiceResult.ok(friend_requests)

    def get_received_requests(
        self,
        receiver_id: int | None,
        status: FriendRequestStatus = FriendRequestStatus.PENDING,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ServiceResult[Sequence[FriendRequest]]:
        """Return all friend requests received by the given user. By default it returns the pending requests."""

        receiver_result = self._require_receiver(receiver_id)

        if not receiver_result.success:
            assert receiver_result.errors is not None
            return ServiceResult.fail(receiver_result.errors)

        assert receiver_id is not None

        friend_requests = self.friend_request_repository.get_by_receiver_id(
            receiver_id, status=status, limit=limit, offset=offset
        )

        return ServiceResult.ok(friend_requests)
