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
from app.models import (
    User,
    Conversation,
    ConversationMember,
    Message,
    Friend,
    FriendRequest,
)

from app.constants import UserStatus, MessageStatus, FriendStatus, FriendRequestStatus
from app.schemas import ServiceResult

from app.validators import RegisterValidator
from app.utils import hash_password

from typing import Sequence


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

        return errors

    def _require_existing_user(
        self, user_id: int | None, field_name: str, entity_name: str
    ) -> ServiceResult[User]:

        if user_id is None:
            return ServiceResult.fail({field_name: f"{entity_name} ID is required."})

        user = self.user_repository.get_by_id(user_id)

        if user is None or user.status == UserStatus.DELETED:
            return ServiceResult.fail({field_name: f"{entity_name} not found."})

        if user.status == UserStatus.BLOCKED:
            return ServiceResult.fail({field_name: f"{entity_name} is blocked."})

        return ServiceResult.ok(user)

    def _require_user(self, user_id: int | None) -> ServiceResult[User]:
        return self._require_existing_user(user_id, "user_id", "User")

    def _require_conversation(
        self, conversation_id: int | None
    ) -> ServiceResult[Conversation]:

        if conversation_id is None:
            return ServiceResult.fail(
                {"conversation_id": "Conversation ID is required."}
            )

        conversation = self.conversation_repository.get_by_id(conversation_id)

        if conversation is None:
            return ServiceResult.fail({"conversation_id": "Conversation not found."})

        return ServiceResult.ok(conversation)

    def _require_membership(
        self, user_id: int | None, conversation_id: int | None
    ) -> ServiceResult[ConversationMember]:

        user_result = self._require_user(user_id)

        if not user_result.success:
            assert user_result.errors is not None
            return ServiceResult.fail(user_result.errors)

        assert user_id is not None

        conversation_result = self._require_conversation(conversation_id)

        if not conversation_result.success:
            assert conversation_result.errors is not None
            return ServiceResult.fail(conversation_result.errors)

        assert conversation_id is not None

        membership = self.conversation_member_repository.get_membership(
            user_id, conversation_id
        )

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
        return self._require_existing_user(friend_id, "friend_id", "Friend")

    def _require_receiver(self, receiver_id: int | None) -> ServiceResult[User]:
        return self._require_existing_user(receiver_id, "receiver_id", "Receiver")

    def _require_friendship(
        self, user_id: int | None, friend_id: int | None
    ) -> ServiceResult[Friend]:

        user_result = self._require_user(user_id)

        if not user_result.success:
            assert user_result.errors is not None
            return ServiceResult.fail(user_result.errors)

        assert user_id is not None

        friend_result = self._require_friend(friend_id)

        if not friend_result.success:
            assert friend_result.errors is not None
            return ServiceResult.fail(friend_result.errors)

        assert friend_id is not None

        friendship = self.friend_repository.get(user_id, friend_id)

        if friendship is None or friendship.status == FriendStatus.REMOVED:
            return ServiceResult.fail({"friendship": "Friendship not found."})

        return ServiceResult.ok(friendship)

    def _require_friend_request_between_users(
        self,
        sender_id: int | None,
        receiver_id: int | None,
        status: FriendRequestStatus | None = None,
    ) -> ServiceResult[FriendRequest]:

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

        friend_request = self.friend_request_repository.get_one(
            sender_id, receiver_id, status
        )

        if friend_request is None:
            return ServiceResult.fail({"friend_request": "Friend request not found."})

        return ServiceResult.ok(friend_request)

    def _require_friend_request(
        self, friend_request_id: int | None
    ) -> ServiceResult[FriendRequest]:

        if friend_request_id is None:
            return ServiceResult.fail(
                {"friend_request_id": "Friend request ID is required."}
            )

        friend_request: FriendRequest | None = self.friend_request_repository.get_by_id(
            friend_request_id
        )

        if friend_request is None:
            return ServiceResult.fail(
                {"friend_request_id": "Friend request not found."}
            )

        return ServiceResult.ok(friend_request)

    def _restore_deleted_user(
        self,
        user: User,
        firstname: str,
        lastname: str,
        phone_number: str,
        password: str,
    ) -> ServiceResult[User]:
        user.firstname = firstname
        user.lastname = lastname
        user.phone_number = phone_number
        user.password = hash_password(password)

        user.status = UserStatus.ACTIVE
        user.failed_attempts = 0
        user.lock_until = None

        for membership in user.conversation_members:
            membership.is_hidden = False

        for friendship in user.friendships:
            friendship.status = FriendStatus.REMOVED

        for friendship in user.friendships_as_friend:
            friendship.status = FriendStatus.REMOVED

        return ServiceResult.ok(user)

    def _change_friend_request_status(
        self,
        sender_id: int | None,
        receiver_id: int | None,
        status: FriendRequestStatus,
    ) -> ServiceResult[FriendRequest]:

        friend_request_result = self._require_friend_request_between_users(
            sender_id, receiver_id, FriendRequestStatus.PENDING
        )

        if not friend_request_result.success:
            assert friend_request_result.errors is not None
            return ServiceResult.fail(friend_request_result.errors)

        assert sender_id is not None
        assert receiver_id is not None
        assert friend_request_result.data is not None

        friend_request = friend_request_result.data

        is_friend = self.friend_repository.exists(sender_id, receiver_id)

        if is_friend:
            return ServiceResult.fail({"friendship": "Friendship already exists."})

        friend_request.status = status

        return ServiceResult.ok(friend_request)

    def _create_friendship(self, user_id: int, friend_id: int) -> ServiceResult[Friend]:

        if user_id == friend_id:
            return ServiceResult.fail(
                {"friendship": "You cannot make yourself friend."}
            )

        friendship = self.friend_repository.get(user_id, friend_id)

        if friendship is not None:

            if friendship.status == FriendStatus.ACTIVE:
                return ServiceResult.fail(
                    {"friendship": "You cannot make friend who is already your friend."}
                )

            friendship.status = FriendStatus.ACTIVE
            return ServiceResult.ok(friendship)

        user_id, friend_id = sorted([user_id, friend_id])

        friendship = Friend(user_id=user_id, friend_id=friend_id)

        friendship = self.friend_repository.create(friendship)

        return ServiceResult.ok(friendship)
