# app/services/conversations_service.py

from app.models import Conversation
from app.services import BaseService

from app.schemas import ServiceResult
from app.constants import ConversationType

from app.validators import ConversationValidator

from typing import Sequence


class ConversationService(BaseService):
    """Provides conversation-related business logic."""

    def create(
        self, name: str | None, conversation_type: str | None
    ) -> ServiceResult[Conversation]:
        """
        Create a new conversation.

        Returns:
            ServiceResult containing the created conversation or validation errors.
        """

        if errors := ConversationValidator.create(name, conversation_type):
            return ServiceResult.fail(errors)

        assert conversation_type is not None

        clean_conversation_type = ConversationType(conversation_type.strip())
        clean_name = name.strip() if name is not None else None

        conversation = Conversation(
            name=clean_name, conversation_type=clean_conversation_type
        )

        conversation = self.conversation_repository.create(conversation)

        return ServiceResult.ok(conversation)

    def get_by_id(self, conversation_id: int | None) -> ServiceResult[Conversation]:
        """Return the conversation with the given ID"""

        return self._require_conversation(conversation_id)

    def search_by_name(
        self,
        user_id: int | None,
        conversation_name: str | None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ServiceResult[Sequence[Conversation]]:
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

        if not result.success:
            assert result.errors is not None
            return ServiceResult.fail(result.errors)

        assert user_id is not None

        group_conversations = self.conversation_repository.search_groups_by_name(
            user_id,
            conversation_name,
            limit=limit,
            offset=offset,
        )

        private_conversations = self.conversation_repository.search_private_by_name(
            user_id,
            conversation_name,
            limit=limit,
            offset=offset,
        )

        conversations = [*group_conversations, *private_conversations]

        return ServiceResult.ok(conversations)

    def rename(
        self, conversation_id: int | None, new_name: str | None
    ) -> ServiceResult[Conversation]:
        """
        Rename a conversation.

        Returns:
            ServiceResult containing the updated conversation or validation errors.
        """

        result = self._require_conversation(conversation_id)

        if not result.success:
            return result

        assert conversation_id is not None
        assert result.data is not None

        conversation = result.data

        if conversation.conversation_type == ConversationType.PRIVATE:
            return ServiceResult.fail(
                {"conversation": "Private conversations cannot have a name."}
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
    ) -> ServiceResult[Sequence[Conversation]]:
        """Return the conversations for the given user ID."""

        result = self._require_user(user_id)

        if not result.success:
            assert result.errors is not None
            return ServiceResult.fail(result.errors)

        assert user_id is not None

        conversations = self.conversation_repository.get_user_conversations(
            user_id, limit, offset
        )

        return ServiceResult.ok(conversations)
