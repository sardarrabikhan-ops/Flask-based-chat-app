# app/services/messages_service.py

from app.models import Message, Conversation, ConversationMember
from app.services import BaseService

from app.constants import (
    MessageStatus,
    MessageDeliveryStatus,
    ConversationMemberRole,
)
from app.validators import MessageValidator
from app.results import ServiceResult, ResultCode, Result, FailureResult

from typing import Sequence
import logging

logger = logging.getLogger(__name__)


class MessageService(BaseService):
    """Provides message-related business logic."""

    def send_in_conversation(
        self,
        sender_id: int | None,
        conversation_id: int | None,
        content: str | None,
    ) -> Result[Message]:
        """
        Send a message to conversation.
        Returns:
            Service Result containing the created message.
        """

        if error := MessageValidator.validate_content(content):
            return ServiceResult.fail({"content": error})

        assert content is not None

        result = self._require_membership(sender_id, conversation_id)

        if isinstance(result, FailureResult):
            return result

        assert conversation_id is not None

        membership = result.data

        if membership.is_archived:
            return ServiceResult.fail(
                {"permission": "You cannot send message to an archived conversation."},
                code=ResultCode.FORBIDDEN,
            )

        message = Message(
            sender_id=sender_id,
            conversation_id=conversation_id,
            content=content.strip(),
        )

        message = self.message_repository.create(message)

        logger.info(
            "User sent a message in conversation. %s %s",
            result.data.user,
            result.data.conversation,
        )
        return ServiceResult.ok(message, code=ResultCode.CREATED)

    def send_private(
        self,
        sender_id: int | None,
        receiver_id: int | None,
        content: str | None,
    ) -> Result[Message]:
        """
        Send a message to conversation.
        Returns:
            Service Result containing the created message.
        """

        if error := MessageValidator.validate_content(content):
            return ServiceResult.fail({"content": error})

        assert content is not None

        result = self._require_user(sender_id)

        if isinstance(result, FailureResult):
            return result

        assert sender_id is not None

        sender = result.data

        result = self._require_receiver(receiver_id)

        if isinstance(result, FailureResult):
            return result

        assert receiver_id is not None

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

            logger.info("Conversation created due to first message. %s", conversation)

        result = self._require_membership(sender_id, conversation.id)

        if isinstance(result, FailureResult):
            return result

        membership = result.data

        if membership.is_archived:
            return ServiceResult.fail(
                {"permission": "User cannot send message to an archived conversation."},
                code=ResultCode.FORBIDDEN,
            )

        receiver_membership = self.conversation_member_repository.get_membership(
            receiver_id,
            conversation.id,
            removed=True,
        )

        assert receiver_membership is not None

        membership.is_hidden = False
        receiver_membership.is_hidden = False

        message = Message(
            sender_id=sender_id,
            conversation_id=conversation.id,
            content=content.strip(),
        )

        message = self.message_repository.create(message)

        logger.info(
            "User sent a message in conversation. %s %s",
            result.data.user,
            result.data.conversation,
        )
        return ServiceResult.ok(message, code=ResultCode.CREATED)

    def get_by_id(self, message_id: int | None) -> Result[Message]:
        """Return the message with the given ID"""

        return self._require_message(message_id)

    def get_conversation_messages(
        self,
        user_id: int | None,
        conversation_id: int | None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Result[Sequence[Message]]:
        """Return the messages with the given conversation ID"""

        result = self._require_membership(user_id, conversation_id)

        if isinstance(result, FailureResult):
            return result

        assert conversation_id is not None

        messages = self.message_repository.get_by_conversation_id(
            conversation_id, MessageStatus.ACTIVE, limit, offset
        )

        return ServiceResult.ok(messages)

    def edit(
        self, user_id: int | None, message_id: int | None, content: str | None
    ) -> Result[Message]:
        """Edit the message content and returns it"""

        user_result = self._require_user(user_id)

        if isinstance(user_result, FailureResult):
            return user_result

        assert user_id is not None

        user = user_result.data

        message_result = self._require_message(message_id)

        if isinstance(message_result, FailureResult):
            return message_result

        message = message_result.data

        if message.sender != user:
            return ServiceResult.fail(
                {"permission": "Only sender can edit message."},
                code=ResultCode.FORBIDDEN,
            )

        if error := MessageValidator.validate_content(content):
            return ServiceResult.fail({"content": error})

        assert content is not None

        if message.content != content.strip():
            message.content = content.strip()

            logger.info(
                "User edited a message. %s %s",
                user_result.data,
                message_result.data,
            )

        return ServiceResult.ok(message)

    def delete(self, user_id: int | None, message_id: int | None) -> Result[Message]:
        """Soft-delete a message by marking its status as DELETED."""

        result = self._require_user(user_id)

        if isinstance(result, FailureResult):
            return result

        assert user_id is not None

        user = result.data

        result = self._require_message(message_id)

        if isinstance(result, FailureResult):
            return result

        message = result.data

        if message.sender != user:
            return ServiceResult.fail(
                {"permission": "Only sender can delete message."},
                code=ResultCode.FORBIDDEN,
            )

        message.status = MessageStatus.DELETED

        logger.info("User deleted a message. %s %s", user, message)
        return ServiceResult.ok(message)

    def mark_delivered(
        self, user_id: int | None, message_id: int | None
    ) -> Result[Message]:
        """Mark the message as delivered."""

        result = self._require_message(message_id)

        if isinstance(result, FailureResult):
            return result

        message = result.data

        result = self._require_membership(user_id, message.conversation_id)

        if isinstance(result, FailureResult):
            return result

        assert user_id is not None

        if message.delivery_status == MessageDeliveryStatus.READ:
            return ServiceResult.fail(
                {"message": "Message cannot be marked delivered after it is read."},
                code=ResultCode.CONFLICT,
            )

        message.delivery_status = MessageDeliveryStatus.DELIVERED

        return ServiceResult.ok(message)

    def mark_read(self, user_id: int | None, message_id: int | None) -> Result[Message]:
        """Mark the message as read."""

        result = self._require_message(message_id)

        if isinstance(result, FailureResult):
            return result

        message = result.data

        result = self._require_membership(user_id, message.conversation_id)

        if isinstance(result, FailureResult):
            return result

        assert user_id is not None

        if message.delivery_status == MessageDeliveryStatus.READ:
            return ServiceResult.fail(
                {"message": "Message cannot be marked read after it is already read."},
                code=ResultCode.CONFLICT,
            )

        message.delivery_status = MessageDeliveryStatus.READ

        return ServiceResult.ok(message)
