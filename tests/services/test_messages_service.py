# tests/services/test_messages_service.py

import pytest

from app.results import FailureResult
from app.services import MessageService

from tests.factories import make_group, make_user


@pytest.fixture()
def service(db_session) -> MessageService:
    return MessageService(db_session)


def test_member_can_send_message_in_conversation(db_session, service):
    alice = make_user(db_session)
    conversation = make_group(db_session, creator=alice)

    result = service.send_in_conversation(
        sender_id=alice.id, conversation_id=conversation.id, content="Hello there"
    )

    assert result.success
    assert result.data.content == "Hello there"


def test_non_member_cannot_send_message_in_conversation(db_session, service):
    alice = make_user(db_session)
    mallory = make_user(db_session)
    conversation = make_group(db_session, creator=alice)

    result = service.send_in_conversation(
        sender_id=mallory.id, conversation_id=conversation.id, content="Hello there"
    )

    assert isinstance(result, FailureResult)


def test_send_private_reuses_existing_conversation_between_same_users(
    db_session, service
):
    alice = make_user(db_session)
    bob = make_user(db_session)

    first = service.send_private(sender_id=alice.id, receiver_id=bob.id, content="Hi Bob")

    db_session.flush()
    second = service.send_private(
        sender_id=bob.id, receiver_id=alice.id, content="Hi Alice"
    )
    db_session.flush()

    assert first.success and second.success
    # A second private message between the same pair must land in the
    # SAME conversation, not create a duplicate one.
    assert first.data.conversation_id == second.data.conversation_id
