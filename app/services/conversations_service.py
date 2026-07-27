# app/services/conversations_service.py

from sqlalchemy.orm import Session

from app.models import Conversation
from app.repositories import ConversationRepository

from app.schemas import ServiceResult
from app.constants import ConversationType, ConversationStatus

from app.validators import ConversationValidator

from typing import Sequence


class ConversationService:
    """Provides conversation-related business logic."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = ConversationRepository(session)

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
        conversation = self.repository.create(conversation)

        return ServiceResult.ok(conversation)

    def get_by_id(self, conversation_id: int | None) -> ServiceResult[Conversation]:
        """Return the conversation with the given ID"""

        if conversation_id is None:
            return ServiceResult.fail(
                {"conversation_id": "Conversation ID is required."}
            )

        conversation = self.repository.get_by_id(conversation_id)

        if conversation is None:
            return ServiceResult.fail({"conversation_id": "Conversation not found."})

        return ServiceResult.ok(conversation)

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

        conversations = self.repository.search_by_name(
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

        if conversation_id is None:
            return ServiceResult.fail(
                {"conversation_id": "Conversation ID is required."}
            )

        conversation = self.repository.get_by_id(conversation_id)

        if conversation is None:
            return ServiceResult.fail({"conversation_id": "Conversation not found."})

        if error := ConversationValidator.name(new_name):
            return ServiceResult.fail({"name": error})

        assert new_name is not None

        conversation.name = new_name.strip()

        return ServiceResult.ok(conversation)

    def delete(self, conversation_id: int | None) -> ServiceResult[Conversation]:
        """Soft-delete a user by marking its status as DELETED."""

        if conversation_id is None:
            return ServiceResult.fail({"conversation_id": "Conversation ID is required."})

        conversation = self.repository.get_by_id(conversation_id)

        if conversation is None:
            return ServiceResult.fail({"conversation_id": "Conversation not found."})

        conversation.status = ConversationStatus.DELETED

        return ServiceResult.ok(conversation)
