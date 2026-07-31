# app/repositories/conversation_members_repo.py

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ConversationMember
from app.constants import ConversationMemberStatus

from typing import Sequence


class ConversationMemberRepository:

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_membership(
        self, user_id: int, conversation_id: int
    ) -> ConversationMember | None:
        statement = select(ConversationMember).where(
            ConversationMember.user_id == user_id,
            ConversationMember.conversation_id == conversation_id,
            ConversationMember.status == ConversationMemberStatus.ACTIVE,
            ConversationMember.deleted_for_user.is_(False),
        )

        return self.session.scalar(statement)

    def get_conversation_members(
        self,
        conversation_id: int,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Sequence[ConversationMember]:

        statement = select(ConversationMember).where(
            ConversationMember.conversation_id == conversation_id,
            ConversationMember.deleted_for_user == False,
            ConversationMember.status == ConversationMemberStatus.ACTIVE,
        )

        if limit is not None:
            statement = statement.limit(limit)

        if offset is not None:
            statement = statement.offset(offset)

        return self.session.scalars(statement).all()

    def create(self, conversation_member: ConversationMember) -> ConversationMember:
        self.session.add(conversation_member)
        return conversation_member
