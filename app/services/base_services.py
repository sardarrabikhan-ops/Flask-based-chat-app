# app/services/base_services.py

from sqlalchemy.orm import Session

from app.repositories import (
    UserRepository,
    ConversationRepository,
    ConversationMemberRepository,
    MessageRepository,
    FriendRepository,
    FriendRequestRepository,
)
from app.models import User

from app.constants import UserStatus
from app.schemas import ServiceResult


class BaseService:

    def __init__(self, session: Session) -> None:
        self.user_repository = UserRepository(session)
        self.conversation_repository = ConversationRepository(session)
        self.conversation_member_repository = ConversationMemberRepository(session)
        self.message_repository = MessageRepository(session)
        self.friend_repository = FriendRepository(session)
        self.friend_request_repository = FriendRequestRepository(session)


    def _require_user(self, user_id: int | None) -> ServiceResult[User]:

        if user_id is None:
            return ServiceResult.fail({"user_id": "User ID is required."})

        user: User | None = self.user_repository.get_by_id(user_id)

        if user is None or user.status == UserStatus.DELETED:
            return ServiceResult.fail({"user_id": "User not found."})

        if user.status == UserStatus.BLOCKED:
            return ServiceResult.fail({"user_id": "User is blocked."})

        return ServiceResult.ok(user)