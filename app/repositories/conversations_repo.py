# app/repositories/conversations_repo.py

from sqlalchemy import select, case, func, union_all
from sqlalchemy.orm import aliased

from app.repositories import BaseRepository
from app.models import Conversation, ConversationMember, User, Message

from app.utils import escape_like
from app.constants import ConversationMemberStatus, ConversationType

from typing import Sequence


class ConversationRepository(BaseRepository):

    def search_by_name(
        self, user_id: int, name: str, limit: int | None, offset: int | None
    ) -> Sequence[Conversation]:

        name = escape_like(name)

        exact = name
        starts = f"{name}%"
        contains = f"%{name}%"

        my_membership = aliased(ConversationMember)
        other_membership = aliased(ConversationMember)

        full_name = User.firstname + " " + User.lastname

        private_rank = case(
            (full_name.ilike(exact, escape="\\"), 0),
            (full_name.ilike(starts, escape="\\"), 1),
            (full_name.ilike(contains, escape="\\"), 2),
            else_=3,
        )

        group_rank = case(
            (Conversation.name.ilike(exact, escape="\\"), 0),
            (Conversation.name.ilike(starts, escape="\\"), 1),
            (Conversation.name.ilike(contains, escape="\\"), 2),
            else_=3,
        )

        group_query = (
            select(
                Conversation.id.label("id"),
                Conversation.name.label("display_name"),
                group_rank.label("rank"),
            )
            .join(ConversationMember, ConversationMember.user_id == user_id)
            .where(
                ConversationMember.user_id == user_id,
                Conversation.conversation_type == ConversationType.GROUP,
                ConversationMember.status == ConversationMemberStatus.ACTIVE,
                ConversationMember.is_archived.is_(False),
                ConversationMember.is_hidden.is_(False),
                Conversation.name.ilike(contains, escape="\\"),
            )
        )

        private_query = (
            select(
                Conversation.id.label("id"),
                full_name.label("display_name"),
                private_rank.label("rank"),
            )
            .join(my_membership, my_membership.conversation_id == Conversation.id)
            .join(other_membership, other_membership.conversation_id == Conversation.id)
            .join(User, User.id == other_membership.user_id)
            .where(
                my_membership.user_id == user_id,
                other_membership.user_id != user_id,
                Conversation.conversation_type == ConversationType.PRIVATE,
                my_membership.status == ConversationMemberStatus.ACTIVE,
                other_membership.status == ConversationMemberStatus.ACTIVE,
                my_membership.is_archived.is_(False),
                my_membership.is_hidden.is_(False),
                full_name.ilike(contains, escape="\\"),
            )
        )

        combined = union_all(group_query, private_query).subquery()

        statement = (
            select(Conversation)
            .join(
                combined,
                Conversation.id == combined.c.id,
            )
            .order_by(
                combined.c.rank,
                combined.c.display_name,
                combined.c.id,
            )
        )

        statement = self._paginate(statement, limit, offset)

        return self.session.scalars(statement).all()

    def get_by_id(self, conversation_id: int) -> Conversation | None:
        return self.session.get(Conversation, conversation_id)

    def get_user_conversations(
        self,
        user_id: int,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Sequence[Conversation]:

        statement = (
            select(Conversation)
            .join(
                ConversationMember,
                ConversationMember.conversation_id == Conversation.id,
            )
            .outerjoin(
                Message,
                Message.conversation_id == Conversation.id,
            )
            .where(
                ConversationMember.user_id == user_id,
                ConversationMember.status == ConversationMemberStatus.ACTIVE,
                ConversationMember.is_hidden.is_(False),
                ConversationMember.is_archived.is_(False),
            )
            .group_by(Conversation.id)
        )

        statement = self._paginate(
            statement, limit, offset, func.max(Message.created_at).desc().nulls_last()
        )

        return self.session.scalars(statement).all()

    def get_private_between_users(
        self, user1_id: int, user2_id: int
    ) -> Conversation | None:

        cm1 = aliased(ConversationMember)
        cm2 = aliased(ConversationMember)

        statement = (
            select(Conversation)
            .join(
                cm1,
                cm1.conversation_id == Conversation.id,
            )
            .join(
                cm2,
                cm2.conversation_id == Conversation.id,
            )
            .where(
                Conversation.conversation_type == ConversationType.PRIVATE,
                cm1.user_id == user1_id,
                cm2.user_id == user2_id,
                cm1.user_id != cm2.user_id,
                cm1.status == ConversationMemberStatus.ACTIVE,
                cm2.status == ConversationMemberStatus.ACTIVE,
            )
        )

        return self.session.scalar(statement)

    def create(self, conversation: Conversation) -> Conversation:
        self.session.add(conversation)
        return conversation
