# app/services/messages_service.py

from app.models import Message, Conversation, ConversationMember
from app.services import BaseService

from app.schemas import ServiceResult
from app.constants import (
    MessageStatus,
    MessageDeliveryStatus,
    ConversationMemberRole,
    MESSAGE_MAX_LENGTH,
)

from typing import Sequence


class MessageService(BaseService):
    """Provides message-related business logic."""

    def send_in_group(
        self, sender_id: int | None, conversation_id: int | None, content: str | None
    ) -> ServiceResult[Message]:
        """
        Send a message to conversation.
        Returns:
            Service Result containing the created message.
        """

        if content is None or not content.strip():
            return ServiceResult.fail({"content": "Message content is required."})

        assert content is not None

        if len(content) > MESSAGE_MAX_LENGTH:
            return ServiceResult.fail(
                {"content": f"Message must not exceed {MESSAGE_MAX_LENGTH} characters."}
            )

        result = self._require_membership(sender_id, conversation_id)

        if not result.success:
            assert result.errors is not None
            return ServiceResult.fail(result.errors)

        assert conversation_id is not None
        assert result.data is not None

        membership = result.data

        assert membership is not None

        if membership.is_archived:
            return ServiceResult.fail(
                {
                    "conversation_id": "User cannot send message to archived conversation."
                }
            )

        message = Message(
            sender_id=sender_id,
            conversation_id=conversation_id,
            content=content.strip(),
        )

        message = self.message_repository.create(message)

        return ServiceResult.ok(message)

    def send_private(
        self,
        sender_id: int | None,
        receiver_id: int | None,
        content: str | None,
    ) -> ServiceResult[Message]:
        """
        Send a message to conversation.
        Returns:
            Service Result containing the created message.
        """

        if content is None or not content.strip():
            return ServiceResult.fail({"content": "Message content is required."})

        assert content is not None

        if len(content) > MESSAGE_MAX_LENGTH:
            return ServiceResult.fail(
                {"content": f"Message must not exceed {MESSAGE_MAX_LENGTH} characters."}
            )

        result = self._require_user(sender_id)

        if not result.success:
            assert result.errors is not None
            return ServiceResult.fail(result.errors)

        assert sender_id is not None
        assert result.data is not None

        sender = result.data

        result = self._require_receiver(receiver_id)

        if not result.success:
            assert result.errors is not None
            return ServiceResult.fail(result.errors)

        assert receiver_id is not None
        assert result.data is not None

        receiver = result.data

        conversation = self.conversation_repository.get_private_between_users(
            sender_id, receiver_id
        )

        if conversation is None:
            conversation = self.conversation_repository.create(Conversation())

            membership = ConversationMember(
                user=sender,
                conversation=conversation,
                role=ConversationMemberRole.MEMBER,
            )
            self.conversation_member_repository.create(membership)

            membership = ConversationMember(
                user=receiver,
                conversation=conversation,
                role=ConversationMemberRole.MEMBER,
            )
            self.conversation_member_repository.create(membership)

        result = self._require_membership(sender_id, conversation.id)

        if not result.success:
            assert result.errors is not None
            return ServiceResult.fail(result.errors)

        assert result.data is not None

        membership = result.data

        assert membership is not None

        if membership.is_archived:
            return ServiceResult.fail(
                {
                    "conversation_id": "User cannot send message to archived conversation."
                }
            )

        receiver_membership = self.conversation_member_repository.get_membership(
            receiver_id,
            conversation.id,
            removed=True,
        )

        assert receiver_membership is not None, "Receiver membership should always exist."

        membership.is_hidden = False
        receiver_membership.is_hidden = False

        message = Message(
            sender_id=sender_id,
            conversation_id=conversation.id,
            content=content.strip(),
        )

        message = self.message_repository.create(message)

        return ServiceResult.ok(message)

    def get_by_id(self, message_id: int | None) -> ServiceResult[Message]:
        """Return the message with the given ID"""

        return self._require_message(message_id)

    def get_conversation_messages(
        self,
        user_id: int | None,
        conversation_id: int | None,
        status: MessageStatus | None = MessageStatus.ACTIVE,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ServiceResult[Sequence[Message]]:
        """Return the messages with the given conversation ID"""

        result = self._require_membership(user_id, conversation_id)

        if not result.success:
            assert result.errors is not None
            return ServiceResult.fail(result.errors)

        assert conversation_id is not None

        messages = self.message_repository.get_by_conversation_id(
            conversation_id, status, limit, offset
        )

        return ServiceResult.ok(messages)

    def edit(
        self, user_id: int | None, message_id: int | None, content: str | None
    ) -> ServiceResult[Message]:
        """Edit the message content and returns it"""

        result = self._require_user(user_id)

        if not result.success:
            assert result.errors is not None
            return ServiceResult.fail(result.errors)

        assert user_id is not None
        assert result.data is not None

        user = result.data

        result = self._require_message(message_id)

        if not result.success:
            return result

        assert result.data is not None

        message = result.data

        if message.sender != user:
            return ServiceResult.fail({"user": "Only sender can edit message."})

        if content is None or not content.strip():
            return ServiceResult.fail({"content": "Content is required."})

        assert content is not None

        if len(content) > MESSAGE_MAX_LENGTH:
            return ServiceResult.fail(
                {"content": f"Message must not exceed {MESSAGE_MAX_LENGTH} characters."}
            )

        if message.content != content.strip():
            message.content = content.strip()

        return ServiceResult.ok(message)

    def delete(
        self, user_id: int | None, message_id: int | None
    ) -> ServiceResult[Message]:
        """Soft-delete a message by marking its status as DELETED."""

        result = self._require_user(user_id)

        if not result.success:
            assert result.errors is not None
            return ServiceResult.fail(result.errors)

        assert user_id is not None
        assert result.data is not None

        user = result.data

        result = self._require_message(message_id)

        if not result.success:
            return result

        assert result.data is not None

        message = result.data

        if message.sender != user:
            return ServiceResult.fail({"user": "Only sender can delete message."})

        message.status = MessageStatus.DELETED

        return ServiceResult.ok(message)

    def mark_delivered(
        self, user_id: int | None, message_id: int | None
    ) -> ServiceResult[Message]:
        """Mark the message as delivered."""

        result = self._require_message(message_id)

        if not result.success:
            return result

        assert result.data is not None

        message = result.data

        result = self._require_membership(user_id, message.conversation_id)

        if not result.success:
            assert result.errors is not None
            return ServiceResult.fail(result.errors)

        assert user_id is not None

        if message.delivery_status == MessageDeliveryStatus.READ:
            return ServiceResult.fail(
                {"message": "Message cannot be marked delivered after it is read."}
            )

        message.delivery_status = MessageDeliveryStatus.DELIVERED

        return ServiceResult.ok(message)

    def mark_read(
        self, user_id: int | None, message_id: int | None
    ) -> ServiceResult[Message]:
        """Mark the message as read."""

        result = self._require_message(message_id)

        if not result.success:
            return result

        assert result.data is not None

        message = result.data

        result = self._require_membership(user_id, message.conversation_id)

        if not result.success:
            assert result.errors is not None
            return ServiceResult.fail(result.errors)

        assert user_id is not None

        if message.delivery_status == MessageDeliveryStatus.READ:
            return ServiceResult.fail(
                {"message": "Message cannot be marked read after it is already read."}
            )

        message.delivery_status = MessageDeliveryStatus.READ

        return ServiceResult.ok(message)
