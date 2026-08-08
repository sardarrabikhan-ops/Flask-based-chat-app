# tests/services/test_friend_requests_service.py
#
# Covers the friend-request state machine and its authorization rules.
# This is the highest-risk area in the project: an earlier version had
# accept/reject wired so that the intended receiver could never actually
# accept a request. These tests pin down the correct (fixed) behavior so
# that bug class cannot silently come back.

import pytest

from app.constants import FriendRequestStatus, FriendStatus
from app.models import Friend
from app.results import FailureResult, ResultCode
from app.services import FriendRequestService

from tests.factories import make_user


@pytest.fixture()
def service(db_session) -> FriendRequestService:
    return FriendRequestService(db_session)


def test_send_creates_pending_request(db_session, service):
    alice = make_user(db_session)
    bob = make_user(db_session)

    result = service.send(sender_id=alice.id, receiver_id=bob.id)

    db_session.flush()

    assert result.success
    assert result.code == ResultCode.CREATED
    assert result.data.sender_id == alice.id
    assert result.data.receiver_id == bob.id
    assert result.data.status == FriendRequestStatus.PENDING


def test_send_to_self_is_rejected(db_session, service):
    alice = make_user(db_session)

    result = service.send(sender_id=alice.id, receiver_id=alice.id)

    db_session.flush()

    assert isinstance(result, FailureResult)


def test_send_when_already_friends_is_rejected(db_session, service):
    alice = make_user(db_session)
    bob = make_user(db_session)
    user_id, friend_id = sorted((alice.id, bob.id))
    db_session.add(
        Friend(user_id=user_id, friend_id=friend_id, status=FriendStatus.ACTIVE)
    )
    db_session.flush()

    result = service.send(sender_id=alice.id, receiver_id=bob.id)

    db_session.flush()

    assert isinstance(result, FailureResult)
    assert result.code == ResultCode.CONFLICT


def test_send_duplicate_pending_request_is_rejected(db_session, service):
    alice = make_user(db_session)
    bob = make_user(db_session)
    service.send(sender_id=alice.id, receiver_id=bob.id)

    result = service.send(sender_id=alice.id, receiver_id=bob.id)

    db_session.flush()

    assert isinstance(result, FailureResult)
    assert result.code == ResultCode.CONFLICT


def test_send_reciprocal_pending_request_is_rejected(db_session, service):
    alice = make_user(db_session)
    bob = make_user(db_session)
    service.send(sender_id=alice.id, receiver_id=bob.id)

    # Bob tries to send one back before Alice's is resolved.
    result = service.send(sender_id=bob.id, receiver_id=alice.id)
    db_session.flush()

    assert isinstance(result, FailureResult)
    assert result.code == ResultCode.CONFLICT


def test_receiver_can_accept_request_and_friendship_is_created(db_session, service):
    alice = make_user(db_session)
    bob = make_user(db_session)
    sent = service.send(sender_id=alice.id, receiver_id=bob.id)
    db_session.flush()

    result = service.accept(friend_request_id=sent.data.id, actor_id=bob.id)

    assert result.success
    assert result.data.status == FriendRequestStatus.ACCEPTED

    user_id, friend_id = sorted((alice.id, bob.id))
    friendship = db_session.get(Friend, (user_id, friend_id))
    assert friendship is not None
    assert friendship.status == FriendStatus.ACTIVE


def test_non_receiver_cannot_accept_request(db_session, service):
    alice = make_user(db_session)
    bob = make_user(db_session)
    mallory = make_user(db_session)
    sent = service.send(sender_id=alice.id, receiver_id=bob.id)
    db_session.flush()

    result = service.accept(friend_request_id=sent.data.id, actor_id=mallory.id)

    assert isinstance(result, FailureResult)
    assert result.code == ResultCode.FORBIDDEN

    # And critically: the sender cannot "accept" their own request either.
    result = service.accept(friend_request_id=sent.data.id, actor_id=alice.id)

    assert isinstance(result, FailureResult)
    assert result.code == ResultCode.FORBIDDEN


def test_receiver_can_reject_request(db_session, service):
    alice = make_user(db_session)
    bob = make_user(db_session)
    sent = service.send(sender_id=alice.id, receiver_id=bob.id)
    db_session.flush()

    result = service.reject(friend_request_id=sent.data.id, actor_id=bob.id)

    assert result.success
    assert result.data.status == FriendRequestStatus.REJECTED


def test_non_receiver_cannot_reject_request(db_session, service):
    alice = make_user(db_session)
    bob = make_user(db_session)
    mallory = make_user(db_session)
    sent = service.send(sender_id=alice.id, receiver_id=bob.id)
    db_session.flush()

    result = service.reject(friend_request_id=sent.data.id, actor_id=mallory.id)

    assert isinstance(result, FailureResult)
    assert result.code == ResultCode.FORBIDDEN


def test_sender_can_cancel_request(db_session, service):
    alice = make_user(db_session)
    bob = make_user(db_session)
    sent = service.send(sender_id=alice.id, receiver_id=bob.id)
    db_session.flush()

    result = service.cancel(friend_request_id=sent.data.id, actor_id=alice.id)

    assert result.success
    assert result.data.status == FriendRequestStatus.CANCELED


def test_non_sender_cannot_cancel_request(db_session, service):
    alice = make_user(db_session)
    bob = make_user(db_session)
    sent = service.send(sender_id=alice.id, receiver_id=bob.id)
    db_session.flush()

    # The receiver cannot cancel -- only the sender can.
    result = service.cancel(friend_request_id=sent.data.id, actor_id=bob.id)

    assert isinstance(result, FailureResult)
    assert result.code == ResultCode.FORBIDDEN


def test_already_processed_request_cannot_be_processed_again(db_session, service):
    alice = make_user(db_session)
    bob = make_user(db_session)
    sent = service.send(sender_id=alice.id, receiver_id=bob.id)
    db_session.flush()
    service.accept(friend_request_id=sent.data.id, actor_id=bob.id)

    # Accepting an already-ACCEPTED request must fail, not silently
    # succeed or create a second/duplicate friendship.
    result = service.accept(friend_request_id=sent.data.id, actor_id=bob.id)

    assert isinstance(result, FailureResult)
    assert result.code == ResultCode.CONFLICT

    user_id, friend_id = sorted((alice.id, bob.id))
    friendship_count = (
        db_session.query(Friend)
        .filter_by(user_id=user_id, friend_id=friend_id)
        .count()
    )
    assert friendship_count == 1
