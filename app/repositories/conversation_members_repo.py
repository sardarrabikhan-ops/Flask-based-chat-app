# app/repositories/conversation_members_repo.py

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import ColumnElement

from app.models import ConversationMember

from typing import Sequence


class ConversationMemberRepository:

    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, user_id: int, conversation_id: int) -> ConversationMember | None:
        statement = select(ConversationMember).where(
            ConversationMember.user_id == user_id,
            ConversationMember.conversation_id == conversation_id,
        )

        return self.session.scalar(statement)

    def get_by_user_id(
        self,
        user_id: int,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Sequence[ConversationMember]:

        statement = select(ConversationMember).where(
            ConversationMember.user_id == user_id
        )

        if limit is not None:
            statement = statement.limit(limit)

        if offset is not None:
            statement = statement.offset(offset)

        return self.session.scalars(statement).all()

    def get_by_conversation_id(
        self,
        conversation_id: int,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Sequence[ConversationMember]:

        statement = select(ConversationMember).where(
            ConversationMember.conversation_id == conversation_id
        )

        if limit is not None:
            statement = statement.limit(limit)

        if offset is not None:
            statement = statement.offset(offset)

        return self.session.scalars(statement).all()

    def create(self, conversation_member: ConversationMember) -> ConversationMember:
        self.session.add(conversation_member)
        return conversation_member

    def delete(self, conversation_member: ConversationMember) -> None:
        self.session.delete(conversation_member)
