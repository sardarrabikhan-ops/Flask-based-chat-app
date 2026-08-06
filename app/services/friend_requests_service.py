# app/services/friend_requests_service.py

from app.models import FriendRequest
from app.services import BaseService

from app.constants import FriendRequestStatus
from app.results import ServiceResult, Result, ResultCode, FailureResult

from typing import Sequence
import logging

logger = logging.getLogger(__name__)


class FriendRequestService(BaseService):
    """Provides friend-request-related business logic."""

    def send(
        self, sender_id: int | None, receiver_id: int | None
    ) -> Result[FriendRequest]:
        """Send a friend request to receiver."""

        if sender_id == receiver_id:
            return ServiceResult.fail(
                {"friend_request": "You cannot send a friend request to yourself."}
            )

        sender_result = self._require_user(sender_id)

        if isinstance(sender_result, FailureResult):
            return sender_result

        assert sender_id is not None

        receiver_result = self._require_receiver(receiver_id)

        if isinstance(receiver_result, FailureResult):
            return receiver_result

        assert receiver_id is not None

        is_friend = self.friend_repository.exists(sender_id, receiver_id)

        if is_friend:
            return ServiceResult.fail(
                {"friendship": "Friendship already exists."}, code=ResultCode.CONFLICT
            )

        is_request = self.friend_request_repository.exists(
            sender_id, receiver_id, FriendRequestStatus.PENDING
        )
        is_reverse_request = self.friend_request_repository.exists(
            receiver_id, sender_id, FriendRequestStatus.PENDING
        )

        if is_request or is_reverse_request:
            return ServiceResult.fail(
                {"friend_request": "A pending friend request already exist."},
                code=ResultCode.CONFLICT,
            )

        friend_request = FriendRequest(sender_id=sender_id, receiver_id=receiver_id)
        friend_request = self.friend_request_repository.create(friend_request)

        logger.info(
            "User sent a friend request to user. %s %s %s",
            sender_result.data,
            receiver_result.data,
            friend_request,
        )
        return ServiceResult.ok(friend_request, code=ResultCode.CREATED)

    def accept(
        self, friend_request_id: int | None, actor_id: int | None
    ) -> Result[FriendRequest]:
        """Accept the friend request by marking it's status as ACCEPTED."""

        result = self._require_friend_request_action(
            friend_request_id,
            actor_id,
            require_sender=False,
        )

        if isinstance(result, FailureResult):
            return result

        friend_request = result.data

        friendship_result = self._create_friendship(
            friend_request.sender_id,
            friend_request.receiver_id,
        )

        if isinstance(friendship_result, FailureResult):
            return friendship_result

        friend_request.status = FriendRequestStatus.ACCEPTED

        logger.info(
            "User accepted a friend request. %s %s %s",
            friend_request.receiver,
            friend_request.sender,
            friend_request,
        )
        return ServiceResult.ok(friend_request)

    def reject(
        self, friend_request_id: int | None, actor_id: int | None
    ) -> Result[FriendRequest]:
        """Reject the friend request by marking it's status as REJECTED."""

        result = self._require_friend_request_action(
            friend_request_id,
            actor_id,
            require_sender=False,
        )

        if isinstance(result, FailureResult):
            return result

        friend_request = result.data

        friend_request.status = FriendRequestStatus.REJECTED

        logger.info(
            "User rejected a friend request from user. %s %s %s",
            friend_request.receiver,
            friend_request.sender,
            friend_request,
        )
        return ServiceResult.ok(friend_request)

    def cancel(
        self, friend_request_id: int | None, actor_id: int | None
    ) -> Result[FriendRequest]:
        """Cancel the friend request by marking it's status as CANCELED."""

        result = self._require_friend_request_action(
            friend_request_id,
            actor_id,
            require_sender=True,
        )

        if isinstance(result, FailureResult):
            return result

        friend_request = result.data

        friend_request.status = FriendRequestStatus.CANCELED

        logger.info(
            "User canceled a friend request. %s %s %s",
            friend_request.sender,
            friend_request.receiver,
            friend_request,
        )
        return ServiceResult.ok(friend_request)

    def get(
        self,
        sender_id: int | None,
        receiver_id: int | None,
        status: FriendRequestStatus = FriendRequestStatus.PENDING,
    ) -> Result[Sequence[FriendRequest]]:
        """Return all the friend request belongs to the sender_id user and receiver_id user. By default it returns the pending requests."""

        sender_result = self._require_user(sender_id)

        if isinstance(sender_result, FailureResult):
            return sender_result

        assert sender_id is not None

        receiver_result = self._require_receiver(receiver_id)

        if isinstance(receiver_result, FailureResult):
            return receiver_result

        assert receiver_id is not None

        friend_requests = self.friend_request_repository.get(
            sender_id, receiver_id, status
        )

        return ServiceResult.ok(friend_requests)

    def get_sent_requests(
        self,
        sender_id: int | None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Result[Sequence[FriendRequest]]:
        """Return all pending friend requests sent by the given user."""

        sender_result = self._require_user(sender_id)

        if isinstance(sender_result, FailureResult):
            return sender_result

        assert sender_id is not None

        friend_requests = self.friend_request_repository.get_by_sender_id(
            sender_id, status=FriendRequestStatus.PENDING, limit=limit, offset=offset
        )

        return ServiceResult.ok(friend_requests)

    def get_received_requests(
        self,
        receiver_id: int | None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Result[Sequence[FriendRequest]]:
        """Return all pending friend requests received by the given user."""

        receiver_result = self._require_receiver(receiver_id)

        if isinstance(receiver_result, FailureResult):
            return receiver_result

        assert receiver_id is not None

        friend_requests = self.friend_request_repository.get_by_receiver_id(
            receiver_id, status=FriendRequestStatus.PENDING, limit=limit, offset=offset
        )

        return ServiceResult.ok(friend_requests)
