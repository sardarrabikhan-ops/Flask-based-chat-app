# app/services/messages_service.py

from app.models import Message
from app.services import BaseService

from app.schemas import ServiceResult
from app.constants import MessageStatus, MessageDeliveryStatus, ConversationStatus

from typing import Sequence


class MessageService(BaseService):
    """Provides message-related business logic."""

    def send(
        self, sender_id: int | None, conversation_id: int | None, content: str | None
    ) -> ServiceResult[Message]:
        """
        Send a message to conversation.
        Returns:
            Service Result containing the created message.
        """

        if content is None or not content.strip():
            return ServiceResult.fail({"content": "Message content is required."})

        result = self._require_membership(sender_id, conversation_id)

        if result.success is False:
            assert result.errors is not None
            return ServiceResult.fail(result.errors)

        assert conversation_id is not None
        assert result.data is not None

        conversation = result.data.conversation

        assert conversation is not None

        if conversation.status == ConversationStatus.ARCHIVED:
            return ServiceResult.fail({"conversation_id": "User cannot send message to archived conversation."})

        message = Message(sender_id=sender_id, conversation_id=conversation_id, content=content.strip())

        message = self.message_repository.create(message)

        return ServiceResult.ok(message)

    def get_by_id(self, message_id: int | None) -> ServiceResult[Message]:
        """Return the message with the given ID"""

        return self._require_message(message_id)

    def get_conversation_messages(
        self,
        user_id: int | None,
        conversation_id: int | None,
        status: MessageStatus | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ServiceResult[Sequence[Message]]:
        """Return the messages with the given conversation ID"""

        result = self._require_membership(user_id, conversation_id)

        if result.success is False:
            assert result.errors is not None
            return ServiceResult.fail(result.errors)

        assert conversation_id is not None

        messages = self.message_repository.get_by_conversation_id(
            conversation_id, status, limit, offset
        )

        if not messages:
            return ServiceResult.fail(
                {"message": "This conversation doesn't contain messages."}
            )

        return ServiceResult.ok(messages)

    def edit(
        self, user_id: int | None, message_id: int | None, content: str | None
    ) -> ServiceResult[Message]:
        """Edit the message content and returns it"""

        result = self._require_user(user_id)

        if result.success is False:
            assert result.errors is not None
            return ServiceResult.fail(result.errors)

        assert user_id is not None
        assert result.data is not None

        user = result.data

        result = self._require_message(message_id)

        if result.success is False:
            return result

        assert result.data is not None

        message = result.data

        if message.sender != user:
            return ServiceResult.fail({"user": "Only sender can edit message."})

        if content is None or not content.strip():
            return ServiceResult.fail({"content": "Content is required."})

        if message.content != content.strip():
            message.content = content.strip()

        return ServiceResult.ok(message)

    def delete(self, user_id: int | None, message_id: int | None) -> ServiceResult[Message]:
        """Soft-delete a message by marking its status as DELETED."""

        result = self._require_user(user_id)

        if result.success is False:
            assert result.errors is not None
            return ServiceResult.fail(result.errors)

        assert user_id is not None
        assert result.data is not None

        user = result.data

        result = self._require_message(message_id)

        if result.success is False:
            return result

        assert result.data is not None

        message = result.data

        if message.sender != user:
            return ServiceResult.fail({"user": "Only sender can delete message."})

        message.status = MessageStatus.DELETED

        return ServiceResult.ok(message)

    def mark_delivered(self, message_id: int | None) -> ServiceResult[Message]:
        """Mark the message as delivered."""

        result = self._require_message(message_id)

        if result.success is False:
            return result

        assert result.data is not None

        message = result.data

        if message.delivery_status == MessageDeliveryStatus.READ:
            return ServiceResult.fail({"message": "Message cannot be marked delivered after it is read."})

        message.delivery_status = MessageDeliveryStatus.DELIVERED

        return ServiceResult.ok(message)

    def mark_read(self, user_id: int | None, message_id: int | None) -> ServiceResult[Message]:
        """Mark the message as read."""

        result = self._require_message(message_id)

        if result.success is False:
            return result

        assert result.data is not None

        message = result.data

        result = self._require_membership(user_id, message.conversation_id)

        if result.success is False:
            assert result.errors is not None
            return ServiceResult.fail(result.errors)

        assert user_id is not None

        if message.delivery_status == MessageDeliveryStatus.READ:
            return ServiceResult.fail({"message": "Message cannot be marked read after it is already read."})

        message.delivery_status = MessageDeliveryStatus.READ

        return ServiceResult.ok(message)
