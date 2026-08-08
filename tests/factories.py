# tests/factories.py

import itertools

from app.constants import ConversationMemberRole, ConversationType, UserStatus
from app.models import Conversation, ConversationMember, User
from app.utils import hash_password

_counter = itertools.count(1)


def make_user(session, **overrides) -> User:
    n = next(_counter)

    defaults = dict(
        firstname="Test",
        lastname=f"User{n}",
        email=f"user{n}@example.com",
        phone_number=f"+1555000{n:04d}",
        password=hash_password("Str0ng!Pass1"),
        status=UserStatus.ACTIVE,
    )
    defaults.update(overrides)

    user = User(**defaults)
    session.add(user)
    session.flush()
    return user


def make_group(session, creator: User, name: str = "Test Group") -> Conversation:
    conversation = Conversation(name=name, conversation_type=ConversationType.GROUP)
    session.add(conversation)
    session.flush()

    membership = ConversationMember(
        user_id=creator.id,
        conversation_id=conversation.id,
        role=ConversationMemberRole.ADMIN,
    )
    session.add(membership)
    session.flush()

    return conversation


def add_member(
    session,
    conversation: Conversation,
    user: User,
    role: ConversationMemberRole = ConversationMemberRole.MEMBER,
) -> ConversationMember:
    membership = ConversationMember(
        user_id=user.id, conversation_id=conversation.id, role=role
    )
    session.add(membership)
    session.flush()
    return membership
