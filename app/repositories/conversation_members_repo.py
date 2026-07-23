# app/repositories/conversation_members_repo.py

from sqlalchemy import select
from sqlalchemy.orm import Session

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

    def get_by_user(self, user_id: int) -> Sequence[ConversationMember]:
        statement = select(ConversationMember).where(
            ConversationMember.user_id == user_id
        )
        return self.session.scalars(statement).all()

    def get_by_conversation(self, conversation_id: int) -> Sequence[ConversationMember]:
        statement = select(ConversationMember).where(
            ConversationMember.conversation_id == conversation_id
        )
        return self.session.scalars(statement).all()

    def create(self, conversation_member: ConversationMember) -> ConversationMember:
        self.session.add(conversation_member)
        return conversation_member

    def delete(self, conversation_member: ConversationMember) -> None:
        self.session.delete(conversation_member)
