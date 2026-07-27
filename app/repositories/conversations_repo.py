# app/repositories/conversations_repo.py

from sqlalchemy import select, or_, case
from sqlalchemy.orm import Session

from app.models import Conversation
from app.constants import ConversationStatus

from typing import Sequence


class ConversationRepository:

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, conversation_id: int) -> Conversation | None:
        return self.session.get(Conversation, conversation_id)

    def search_by_name(
        self,
        conversation_name: str,
        status: ConversationStatus | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Sequence[Conversation]:

        exact = conversation_name
        starts = f"{conversation_name}%"
        contains = f"%{conversation_name}%"

        rank = case(
            (Conversation.name.ilike(exact), 0),
            (Conversation.name.ilike(starts), 1),
            (Conversation.name.ilike(contains), 2),
            else_=3,
        )

        statement = (
            select(Conversation)
            .where(Conversation.name.ilike(contains))
            .order_by(rank, Conversation.name)
        )

        if status is not None:
            statement = statement.where(Conversation.status == status)

        if limit is not None:
            statement = statement.limit(limit)

        if offset is not None:
            statement = statement.offset(offset)

        return self.session.scalars(statement).all()

    def create(self, conversation: Conversation) -> Conversation:
        self.session.add(conversation)
        return conversation
