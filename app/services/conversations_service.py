# app/services/conversations_service.py

from app.models import Conversation, ConversationMember
from app.services import BaseService

from app.constants import (
    ConversationType,
    ConversationMemberRole,
)

from app.validators import ConversationValidator
from app.results import ServiceResult, Result, ResultCode, FailureResult

from typing import Sequence


class ConversationService(BaseService):
    """Provides conversation-related business logic."""

    def create_group(
        self, actor_id: int | None, name: str | None
    ) -> Result[Conversation]:
        """
        Create a new conversation.

        Returns:
            ServiceResult containing the created conversation or validation errors.
        """

        if error := ConversationValidator.name(name):
            return ServiceResult.fail({"name": error})

        assert name is not None

        actor_result = self._require_user(actor_id)

        if isinstance(actor_result, FailureResult):
            return actor_result

        assert actor_id is not None

        conversation = Conversation(
            name=name.strip(),
            conversation_type=ConversationType.GROUP,
        )

        conversation = self.conversation_repository.create(conversation)

        membership = ConversationMember(
            user_id=actor_id,
            conversation_id=conversation.id,
            role=ConversationMemberRole.ADMIN,
        )

        self.conversation_member_repository.create(membership)

        return ServiceResult.ok(conversation, code=ResultCode.CREATED)

    def get_by_id(self, conversation_id: int | None) -> Result[Conversation]:
        """Return the conversation with the given ID"""

        return self._require_conversation(conversation_id)

    def search_by_name(
        self,
        user_id: int | None,
        conversation_name: str | None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Result[Sequence[Conversation]]:
        """Search the conversations with the given name"""

        if conversation_name is None:
            return ServiceResult.fail(
                {"conversation_name": "Conversation name is required."}
            )

        conversation_name = " ".join(conversation_name.split())

        if not conversation_name:
            return ServiceResult.fail(
                {"conversation_name": "Conversation name is required."}
            )

        result = self._require_user(user_id)

        if isinstance(result, FailureResult):
            return result

        assert user_id is not None

        conversations = self.conversation_repository.search_by_name(
            user_id, conversation_name, limit, offset
        )

        return ServiceResult.ok(conversations)

    def rename(
        self,
        actor_id: int | None,
        conversation_id: int | None,
        new_name: str | None,
    ) -> Result[Conversation]:
        """
        Rename a conversation.

        Returns:
            ServiceResult containing the updated conversation or validation errors.
        """

        actor_membership_result = self._require_membership(actor_id, conversation_id)

        if isinstance(actor_membership_result, FailureResult):
            return actor_membership_result

        actor_membership = actor_membership_result.data
        conversation = actor_membership.conversation

        if conversation.conversation_type == ConversationType.PRIVATE:
            return ServiceResult.fail(
                {"conversation": "Private conversations cannot have a name."}
            )

        if actor_membership.role != ConversationMemberRole.ADMIN:
            return ServiceResult.fail(
                {"permission": "Only administrators can rename conversation."},
                code=ResultCode.FORBIDDEN,
            )

        if error := ConversationValidator.name(new_name):
            return ServiceResult.fail({"name": error})

        assert new_name is not None

        conversation.name = new_name.strip()

        return ServiceResult.ok(conversation)

    def get_user_conversations(
        self,
        user_id: int | None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Result[Sequence[Conversation]]:
        """Return the conversations for the given user ID."""

        result = self._require_user(user_id)

        if isinstance(result, FailureResult):
            return result

        assert user_id is not None

        conversations = self.conversation_repository.get_user_conversations(
            user_id, limit, offset
        )

        return ServiceResult.ok(conversations)

    def archive(
        self, conversation_id: int | None, user_id: int | None
    ) -> Result[ConversationMember]:
        """Archive the membership of the given ID's."""

        result = self._require_membership(user_id, conversation_id)

        if isinstance(result, FailureResult):
            return result

        membership = result.data

        membership.is_archived = True

        return ServiceResult.ok(membership)

    def delete(
        self, conversation_id: int | None, user_id: int | None
    ) -> Result[ConversationMember]:
        """Soft-delete the membership of the given ID's."""

        result = self._require_membership(user_id, conversation_id)

        if isinstance(result, FailureResult):
            return result

        membership = result.data

        membership.is_hidden = True

        return ServiceResult.ok(membership)
