# app/services/messages_service.py

from sqlalchemy.orm import Session

from app.models import Message
from app.services import BaseService

from app.schemas import ServiceResult
from app.constants import MessageStatus, MessageDeliveryStatus, UserStatus, ConversationStatus

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

        if sender_id is None:
            return ServiceResult.fail({"sender_id": "Sender ID is required."})

        if conversation_id is None:
            return ServiceResult.fail(
                {"conversation_id": "Conversation ID is required."}
            )

        if content is None or not content.strip():
            return ServiceResult.fail({"content": "Message content is required."})

        user = self.user_repository.get_by_id(sender_id)

        if user is None or user.status == UserStatus.DELETED:
            return ServiceResult.fail({"sender_id": "Sender not found."})

        if user.status == UserStatus.BLOCKED:
            return ServiceResult.fail({"sender_id": "Sender is blocked."})

        conversation = self.conversation_repository.get_by_id(conversation_id)

        if conversation is None or conversation.status == ConversationStatus.DELETED:
            return ServiceResult.fail({"conversation_id": "Conversation not found."})

        membership = self.conversation_member_repository.get(sender_id, conversation_id)

        if membership is None:
            return ServiceResult.fail({"membership": "User doesn't belong to this conversation."})

        message = Message(sender_id=sender_id, conversation_id=conversation_id, content=content.strip())
        message = self.message_repository.create(message)

        return ServiceResult.ok(message)

    def get_by_id(self, message_id: int | None) -> ServiceResult[Message]:
        """Return the message with the given ID"""

        if message_id is None:
            return ServiceResult.fail({"message_id": "Message ID is required."})

        message = self.message_repository.get_by_id(message_id)

        if message is None or message.status == MessageStatus.DELETED:
            return ServiceResult.fail({"message_id": "Message not found."})

        return ServiceResult.ok(message)

    def get_conversation_messages(
        self,
        user_id: int | None,
        conversation_id: int | None,
        status: MessageStatus | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ServiceResult[Sequence[Message]]:
        """Return the messages with the given conversation ID"""

        if conversation_id is None:
            return ServiceResult.fail(
                {"conversation_id": "Conversation ID is required."}
            )

        if user_id is None:
            return ServiceResult.fail({"user_id": "User ID is required."})

        user = self.user_repository.get_by_id(user_id)

        if user is None or user.status == UserStatus.DELETED:
            return ServiceResult.fail({"user_id": "User not found."})

        if user.status == UserStatus.BLOCKED:
            return ServiceResult.fail({"user_id": "User is blocked."})

        conversation = self.conversation_repository.get_by_id(conversation_id)

        if conversation is None:
            return ServiceResult.fail({"conversation_id": "Conversation not found."})

        membership = self.conversation_member_repository.get(user_id, conversation_id)

        if membership is None:
            return ServiceResult.fail({"membership": "User doesn't belong to the message's conversation."})

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

        if message_id is None:
            return ServiceResult.fail({"message_id": "Message ID is required."})

        if user_id is None:
            return ServiceResult.fail({"user_id": "User ID is required."})

        user = self.user_repository.get_by_id(user_id)

        if user is None or user.status == UserStatus.DELETED:
            return ServiceResult.fail({"user_id": "User not found."})

        if user.status == UserStatus.BLOCKED:
            return ServiceResult.fail({"user_id": "User is blocked."})

        message = self.message_repository.get_by_id(message_id)

        if message is None or message.status == MessageStatus.DELETED:
            return ServiceResult.fail({"message_id": "Message not found."})

        if message.sender != user:
            return ServiceResult.fail({"user": "Only sender can edit message."})

        if not content or not content.strip():
            return ServiceResult.fail({"content": "Content is required."})

        if message.content != content.strip():
            message.content = content.strip()

        return ServiceResult.ok(message)

    def delete(self, user_id: int | None, message_id: int | None) -> ServiceResult[Message]:
        """Soft-delete a user by marking its status as DELETED."""

        if message_id is None:
            return ServiceResult.fail({"message_id": "Message ID is required."})

        if user_id is None:
            return ServiceResult.fail({"user_id": "User ID is required."})

        user = self.user_repository.get_by_id(user_id)

        if user is None or user.status == UserStatus.DELETED:
            return ServiceResult.fail({"user_id": "User not found."})

        if user.status == UserStatus.BLOCKED:
            return ServiceResult.fail({"user_id": "User is blocked."})

        message = self.message_repository.get_by_id(message_id)

        if message is None or message.status == MessageStatus.DELETED:
            return ServiceResult.fail({"message_id": "Message not found."})

        if message.sender != user:
            return ServiceResult.fail({"user": "Only sender can edit message."})

        message.status = MessageStatus.DELETED

        return ServiceResult.ok(message)

    def mark_delivered(self, message_id: int | None) -> ServiceResult[Message]:
        """Mark the message as delivered."""

        if message_id is None:
            return ServiceResult.fail({"message_id": "Message ID is required."})

        message = self.message_repository.get_by_id(message_id)

        if message is None or message.status == MessageStatus.DELETED:
            return ServiceResult.fail({"message_id": "Message not found."})

        if message.delivery_status == MessageDeliveryStatus.READ:
            return ServiceResult.fail({"message": "Message cannot be marked delivered after it is read."})

        message.delivery_status = MessageDeliveryStatus.DELIVERED

        return ServiceResult.ok(message)

    def mark_read(self, user_id: int | None, message_id: int | None) -> ServiceResult[Message]:
        """Mark the message as read."""

        if message_id is None:
            return ServiceResult.fail({"message_id": "Message ID is required."})

        message = self.message_repository.get_by_id(message_id)

        if message is None or message.status == MessageStatus.DELETED:
            return ServiceResult.fail({"message_id": "Message not found."})

        if user_id is None:
            return ServiceResult.fail({"user_id": "User ID is required."})

        user = self.user_repository.get_by_id(user_id)

        if user is None or user.status == UserStatus.DELETED:
            return ServiceResult.fail({"user_id": "User not found."})

        if user.status == UserStatus.BLOCKED:
            return ServiceResult.fail({"user_id": "User is blocked."})

        if message.delivery_status == MessageDeliveryStatus.READ:
            return ServiceResult.fail({"message": "Message cannot be marked read after it is already read."})

        membership = self.conversation_member_repository.get(user_id, message.conversation_id)

        if membership is None:
            return ServiceResult.fail({"membership": "User doesn't belong to this message's conversation."})

        message.delivery_status = MessageDeliveryStatus.READ

        return ServiceResult.ok(message)
