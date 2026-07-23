# app/repositories/friend_requests_repo.py

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import FriendRequest
from app.constants import FriendRequestStatus

from typing import Sequence


class FriendRequestRepository:

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, friend_id: int) -> FriendRequest | None:
        return self.session.get(FriendRequest, friend_id)

    def get_by_sender_id(self, sender_id: int) -> Sequence[FriendRequest]:
        statement = select(FriendRequest).where(FriendRequest.sender_id == sender_id)
        return self.session.scalars(statement).all()

    def get_pending_by_sender_id(self, sender_id: int) -> Sequence[FriendRequest]:
        statement = select(FriendRequest).where(
            FriendRequest.sender_id == sender_id,
            FriendRequest.status == FriendRequestStatus.PENDING.value,
        )
        return self.session.scalars(statement).all()

    def get_by_receiver_id(self, receiver_id: int) -> Sequence[FriendRequest]:
        statement = select(FriendRequest).where(
            FriendRequest.receiver_id == receiver_id
        )
        return self.session.scalars(statement).all()

    def get_pending_by_receiver_id(
        self, receiver_id: int
    ) -> Sequence[FriendRequest] | None:
        statement = select(FriendRequest).where(
            FriendRequest.receiver_id == receiver_id,
            FriendRequest.status == FriendRequestStatus.PENDING.value,
        )
        return self.session.scalars(statement).all()

    def create(self, friend_request: FriendRequest) -> FriendRequest | None:
        self.session.add(friend_request)
        return friend_request
