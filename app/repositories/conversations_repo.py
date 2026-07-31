# app/repositories/conversations_repo.py

from sqlalchemy import select, case, func, or_
from sqlalchemy.orm import Session, aliased

from app.models import Conversation, ConversationMember, User, Message
from app.utils import escape_like
from app.constants import ConversationMemberStatus, ConversationType

from typing import Sequence


class ConversationRepository:

    def __init__(self, session: Session) -> None:
        self.session = session

    def search_groups_by_name(
        self,
        user_id: int,
        conversation_name: str,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Sequence[Conversation]:

        conversation_name = escape_like(conversation_name)

        exact = conversation_name
        starts = f"{conversation_name}%"
        contains = f"%{conversation_name}%"

        rank = case(
            (Conversation.name.ilike(exact, escape="\\"), 0),
            (Conversation.name.ilike(starts, escape="\\"), 1),
            (Conversation.name.ilike(contains, escape="\\"), 2),
            else_=3,
        )

        statement = (
            select(Conversation)
            .distinct()
            .join(ConversationMember)
            .where(
                ConversationMember.user_id == user_id,
                Conversation.conversation_type == ConversationType.GROUP,
                ConversationMember.status == ConversationMemberStatus.ACTIVE,
                ConversationMember.is_archived.is_(False),
                ConversationMember.deleted_for_user.is_(False),
                Conversation.name.ilike(contains, escape="\\"),
            )
            .order_by(rank, Conversation.name)
        )

        if limit is not None:
            statement = statement.limit(limit)

        if offset is not None:
            statement = statement.offset(offset)

        return self.session.scalars(statement).all()

    def search_private_by_name(
        self,
        user_id: int,
        name: str,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Sequence[Conversation]:

        name = escape_like(name)

        my_membership = aliased(ConversationMember)
        other_membership = aliased(ConversationMember)

        exact = name
        starts = f"{name}%"
        contains = f"%{name}%"

        full_name = func.concat(User.firstname, " ", User.lastname)
        full_name_reverse = func.concat(User.lastname, " ", User.firstname)

        rank = case(
            (full_name.ilike(exact, escape="\\"), 0),
            (full_name.ilike(starts, escape="\\"), 1),
            (full_name.ilike(contains, escape="\\"), 2),
            (full_name_reverse.ilike(exact, escape="\\"), 3),
            (full_name_reverse.ilike(starts, escape="\\"), 4),
            (full_name_reverse.ilike(contains, escape="\\"), 5),
            else_=6,
        )

        statement = (
            select(Conversation)
            .distinct()
            .join(my_membership, my_membership.conversation_id == Conversation.id)
            .join(other_membership, other_membership.conversation_id == Conversation.id)
            .join(User, User.id == other_membership.user_id)
            .where(
                my_membership.user_id == user_id,
                other_membership.user_id != user_id,
                Conversation.conversation_type == ConversationType.PRIVATE,
                or_(
                    full_name.ilike(contains, escape="\\"),
                    full_name_reverse.ilike(contains, escape="\\"),
                ),
            )
            .where(
                my_membership.status == ConversationMemberStatus.ACTIVE,
                other_membership.status == ConversationMemberStatus.ACTIVE,
                my_membership.is_archived.is_(False),
                my_membership.deleted_for_user.is_(False),
            )
            .order_by(rank, User.firstname, User.lastname, Conversation.id)
        )

        if limit is not None:
            statement = statement.limit(limit)

        if offset is not None:
            statement = statement.offset(offset)

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
                ConversationMember.deleted_for_user.is_(False),
                ConversationMember.is_archived.is_(False),
            )
            .group_by(Conversation.id)
            .order_by(func.max(Message.created_at).desc().nulls_last())
        )

        if limit is not None:
            statement = statement.limit(limit)

        if offset is not None:
            statement = statement.offset(offset)

        return self.session.scalars(statement).all()

    def create(self, conversation: Conversation) -> Conversation:
        self.session.add(conversation)
        return conversation
