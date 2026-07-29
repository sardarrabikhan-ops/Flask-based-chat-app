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
from app.models import User, Conversation, ConversationMember, Message, Friend

from app.constants import UserStatus, ConversationStatus, MessageStatus, FriendStatus
from app.schemas import ServiceResult

from app.validators import RegisterValidator


class BaseService:

    def __init__(self, session: Session) -> None:
        self.user_repository = UserRepository(session)
        self.conversation_repository = ConversationRepository(session)
        self.conversation_member_repository = ConversationMemberRepository(session)
        self.message_repository = MessageRepository(session)
        self.friend_repository = FriendRepository(session)
        self.friend_request_repository = FriendRequestRepository(session)

    def _validate_register_inputs(
        self,
        firstname: str | None,
        lastname: str | None,
        email: str | None,
        phone_number: str | None,
        password: str | None,
    ) -> dict[str, str]:

        errors: dict[str, str] = {}

        # Validation
        if error := RegisterValidator.firstname(firstname):
            errors["firstname"] = error

        if error := RegisterValidator.lastname(lastname):
            errors["lastname"] = error

        if error := RegisterValidator.email_address(email):
            errors["email"] = error

        if error := RegisterValidator.phone_number(phone_number):
            errors["phone_number"] = error

        if error := RegisterValidator.password(password):
            errors["password"] = error

        if errors:
            return errors

        return {}

    def _require_user(self, user_id: int | None) -> ServiceResult[User]:

        if user_id is None:
            return ServiceResult.fail({"user_id": "User ID is required."})

        user: User | None = self.user_repository.get_by_id(user_id)

        if user is None or user.status == UserStatus.DELETED:
            return ServiceResult.fail({"user_id": "User not found."})

        if user.status == UserStatus.BLOCKED:
            return ServiceResult.fail({"user_id": "User is blocked."})

        return ServiceResult.ok(user)

    def _require_conversation(
        self, conversation_id: int | None
    ) -> ServiceResult[Conversation]:

        if conversation_id is None:
            return ServiceResult.fail(
                {"conversation_id": "Conversation ID is required."}
            )

        conversation = self.conversation_repository.get_by_id(conversation_id)

        if conversation is None or conversation.status == ConversationStatus.DELETED:
            return ServiceResult.fail({"conversation_id": "Conversation not found."})

        return ServiceResult.ok(conversation)

    def _require_membership(
        self, user_id: int | None, conversation_id: int | None
    ) -> ServiceResult[ConversationMember]:

        user_result = self._require_user(user_id)

        if user_result.success is False:
            assert user_result.errors is not None
            return ServiceResult.fail(user_result.errors)

        assert user_id is not None

        conversation_result = self._require_conversation(conversation_id)

        if conversation_result.success is False:
            assert conversation_result.errors is not None
            return ServiceResult.fail(conversation_result.errors)

        assert conversation_id is not None

        membership = self.conversation_member_repository.get(user_id, conversation_id)

        if membership is None:
            return ServiceResult.fail({"membership": "Membership not found."})

        return ServiceResult.ok(membership)

    def _require_message(self, message_id: int | None) -> ServiceResult[Message]:

        if message_id is None:
            return ServiceResult.fail({"message_id": "Message ID is required."})

        message = self.message_repository.get_by_id(message_id)

        if message is None or message.status == MessageStatus.DELETED:
            return ServiceResult.fail({"message_id": "Message not found."})

        return ServiceResult.ok(message)


    def _require_friend(self, friend_id: int | None) -> ServiceResult[User]:

        if friend_id is None:
            return ServiceResult.fail({"friend_id": "Friend ID is required."})

        friend: User | None = self.user_repository.get_by_id(friend_id)

        if friend is None or friend.status == UserStatus.DELETED:
            return ServiceResult.fail({"friend_id": "Friend not found."})

        if friend.status == UserStatus.BLOCKED:
            return ServiceResult.fail({"friend_id": "Friend is blocked."})

        return ServiceResult.ok(friend)

    def _require_friendship(
        self, user_id: int | None, friend_id: int | None
    ) -> ServiceResult[Friend]:

        user_result = self._require_user(user_id)

        if user_result.success is False:
            assert user_result.errors is not None
            return ServiceResult.fail(user_result.errors)

        assert user_id is not None

        friend_result = self._require_friend(friend_id)

        if friend_result.success is False:
            assert friend_result.errors is not None
            return ServiceResult.fail(friend_result.errors)

        assert friend_id is not None

        user_id, friend_id = sorted([user_id, friend_id])

        friendship = self.friend_repository.get(user_id, friend_id)

        if friendship is None or friendship.status == FriendStatus.REMOVED:
            return ServiceResult.fail({"friendship": "Friendship not found."})

        return ServiceResult.ok(friendship)