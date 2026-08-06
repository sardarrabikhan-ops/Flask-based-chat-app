# app/repositories/friend_requests_repo.py

from sqlalchemy import select

from app.repositories import BaseRepository
from app.models import FriendRequest
from app.constants import FriendRequestStatus

from typing import Sequence


class FriendRequestRepository(BaseRepository):

    def get_by_id(self, friend_request_id: int) -> FriendRequest | None:
        return self.session.get(FriendRequest, friend_request_id)

    def get(
        self,
        sender_id: int,
        receiver_id: int,
        status: FriendRequestStatus | None = None,
    ) -> Sequence[FriendRequest]:
        statement = select(FriendRequest).where(
            FriendRequest.sender_id == sender_id,
            FriendRequest.receiver_id == receiver_id,
        )

        if status is not None:
            statement = statement.where(FriendRequest.status == status)

        return self.session.scalars(statement).all()

    def exists(
        self,
        sender_id: int,
        receiver_id: int,
        status: FriendRequestStatus | None = None,
    ) -> bool:
        statement = select(FriendRequest).where(
            FriendRequest.sender_id == sender_id,
            FriendRequest.receiver_id == receiver_id,
        )

        if status is not None:
            statement = statement.where(FriendRequest.status == status)

        return bool(self.session.scalars(statement).first())

    def get_by_sender_id(
        self,
        sender_id: int,
        status: FriendRequestStatus | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Sequence[FriendRequest]:
        statement = select(FriendRequest).where(FriendRequest.sender_id == sender_id)

        if status is not None:
            statement = statement.where(FriendRequest.status == status)

        statement = self._paginate(statement, limit, offset)

        return self.session.scalars(statement).all()

    def get_by_receiver_id(
        self,
        receiver_id: int,
        status: FriendRequestStatus | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Sequence[FriendRequest]:
        statement = select(FriendRequest).where(
            FriendRequest.receiver_id == receiver_id
        )

        if status is not None:
            statement = statement.where(FriendRequest.status == status)

        statement = self._paginate(statement, limit, offset)

        return self.session.scalars(statement).all()

    def create(self, friend_request: FriendRequest) -> FriendRequest:
        self.session.add(friend_request)
        return friend_request
