# tests/services/test_users_service.py

import pytest

from app.constants import FriendRequestStatus, UserStatus
from app.models import ConversationMember
from app.services.friend_requests_service import FriendRequestService
from app.services.users_service import UserService
from app.results import FailureResult

from tests.factories import make_group, make_user


@pytest.fixture()
def service(db_session) -> UserService:
    return UserService(db_session)


def test_delete_marks_user_deleted_and_hides_their_memberships(db_session, service):
    alice = make_user(db_session)
    conversation = make_group(db_session, creator=alice)

    result = service.delete(user_id=alice.id)

    assert result.success
    assert alice.status == UserStatus.DELETED

    membership = db_session.get(ConversationMember, (alice.id, conversation.id))
    assert membership.is_hidden is True


def test_delete_cancels_users_own_pending_sent_friend_requests(db_session, service):
    alice = make_user(db_session)
    bob = make_user(db_session)
    sent = FriendRequestService(db_session).send(sender_id=alice.id, receiver_id=bob.id)
    db_session.flush()

    service.delete(user_id=alice.id)

    # NOTE: intentionally not using db_session.refresh() here -- refresh()
    # discards pending in-memory changes and reloads from the DB, which
    # would silently mask this assertion if delete() hadn't flushed yet.
    # The identity map already gives us the same, mutated object.
    db_session.flush()
    assert sent.success
    assert not isinstance(sent, FailureResult)
    assert sent.data.status == FriendRequestStatus.CANCELED
