# app/repositories/conversation_members_repo.py

from sqlalchemy import select

from app.repositories import BaseRepository
from app.models import ConversationMember
from app.constants import ConversationMemberStatus

from typing import Sequence


class ConversationMemberRepository(BaseRepository):

    def get_membership(
        self,
        user_id: int,
        conversation_id: int,
        removed: bool = False
    ) -> ConversationMember | None:
        statement = select(ConversationMember).where(
            ConversationMember.user_id == user_id,
            ConversationMember.conversation_id == conversation_id,
            ConversationMember.is_hidden.is_(False),
        )

        if not removed:
            statement = statement.where(ConversationMember.status != ConversationMemberStatus.REMOVED)

        return self.session.scalar(statement)

    def get_conversation_members(
        self,
        conversation_id: int,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Sequence[ConversationMember]:

        statement = select(ConversationMember).where(
            ConversationMember.conversation_id == conversation_id,
            ConversationMember.is_hidden == False,
            ConversationMember.status == ConversationMemberStatus.ACTIVE,
        )

        statement = self._paginate(statement, limit, offset)

        return self.session.scalars(statement).all()

    def create(self, conversation_member: ConversationMember) -> ConversationMember:
        self.session.add(conversation_member)
        return conversation_member
