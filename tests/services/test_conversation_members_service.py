# tests/services/test_conversation_members_service.py
#
# Covers the conversation-membership authorization boundary. An earlier
# version of this project let any authenticated user list or probe the
# membership of a conversation they were not part of. These tests pin
# down that only actual members can see membership data.

import pytest

from app.results import FailureResult
from app.services import ConversationMemberService

from tests.factories import add_member, make_group, make_user


@pytest.fixture()
def service(db_session) -> ConversationMemberService:
    return ConversationMemberService(db_session)


def test_member_can_view_conversation_members(db_session, service):
    alice = make_user(db_session)
    bob = make_user(db_session)
    conversation = make_group(db_session, creator=alice)
    add_member(db_session, conversation, bob)

    result = service.get_conversation_members(
        conversation_id=conversation.id, actor_id=alice.id
    )

    assert result.success
    member_ids = {member.id for member in result.data}
    assert member_ids == {alice.id, bob.id}


def test_non_member_cannot_view_conversation_members(db_session, service):
    alice = make_user(db_session)
    mallory = make_user(db_session)
    conversation = make_group(db_session, creator=alice)

    result = service.get_conversation_members(
        conversation_id=conversation.id, actor_id=mallory.id
    )

    assert isinstance(result, FailureResult)


def test_non_member_cannot_look_up_a_specific_member(db_session, service):
    alice = make_user(db_session)
    mallory = make_user(db_session)
    conversation = make_group(db_session, creator=alice)

    result = service.get_member(
        user_id=alice.id, conversation_id=conversation.id, actor_id=mallory.id
    )

    assert isinstance(result, FailureResult)
