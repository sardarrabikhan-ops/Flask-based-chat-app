# app/services/conversations_service.py

from app.models import Conversation
from app.services import BaseService

from app.schemas import ServiceResult
from app.constants import ConversationType, ConversationStatus

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
            return ServiceResult.fail({"conversation_name": "Conversation name is required."})

        conversations = self.conversation_repository.search_by_name(
            conversation_name,
            status=ConversationStatus.ACTIVE,
            limit=limit,
            offset=offset,
        )

        if not conversations:
            return ServiceResult.fail({"conversation_name": "Conversation not found."})

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

        if result.success is False:
            return result

        assert conversation_id is not None
        assert result.data is not None

        conversation = result.data

        if error := ConversationValidator.name(new_name):
            return ServiceResult.fail({"name": error})

        assert new_name is not None

        conversation.name = new_name.strip()

        return ServiceResult.ok(conversation)

    def delete(self, conversation_id: int | None) -> ServiceResult[Conversation]:
        """Soft-delete a conversation by marking its status as DELETED."""

        result = self._require_conversation(conversation_id)

        if result.success is False:
            return result

        assert conversation_id is not None
        assert result.data is not None

        conversation = result.data

        conversation.status = ConversationStatus.DELETED

        return ServiceResult.ok(conversation)
