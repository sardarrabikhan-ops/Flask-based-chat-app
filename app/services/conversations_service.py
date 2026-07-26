# app/services/conversations_service.py

from sqlalchemy.orm import Session

from app.models import Conversation
from app.repositories import ConversationRepository

from app.schemas import ServiceResult
from app.constants import ConversationType

from app.validators import ConversationCreationValidator


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
        errors: dict[str, str] = {}

        if error := ConversationCreationValidator.name(name):
            errors["name"] = error

        if error := ConversationCreationValidator.conversation_type(conversation_type):
            errors["conversation_type"] = error

        if errors:
            return ServiceResult.fail(errors)

        assert name is not None
        assert conversation_type is not None

        name = name.strip()
        conversation_type = conversation_type.strip()

        conversation = Conversation(
            name=name, conversation_type=ConversationType(conversation_type)
        )
        conversation = self.repository.create(conversation)

        return ServiceResult.ok(conversation)
