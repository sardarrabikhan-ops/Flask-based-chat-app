# app/repositories/conversations_repo.py

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Conversation
from app.constants import ConversationStatus

from typing import Sequence


class ConversationRepository:

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, conversation_id: int) -> Conversation | None:
        return self.session.get(Conversation, conversation_id)

    def get_by_name(self, conversation_name: str) -> Sequence[Conversation]:
        statement = select(Conversation).where(Conversation.name == conversation_name)
        return self.session.scalars(statement).all()

    def get_active_by_name(
        self, conversation_name: str
    ) -> Sequence[Conversation]:
        statement = select(Conversation).where(
            Conversation.name == conversation_name,
            Conversation.status != ConversationStatus.DELETED.value,
        )
        return self.session.scalars(statement).all()

    def create(self, conversation: Conversation) -> Conversation:
        self.session.add(conversation)
        return conversation
