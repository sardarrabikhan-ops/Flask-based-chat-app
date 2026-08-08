# tests/services/test_authentication_service.py

from datetime import UTC, datetime

import pytest

from app.constants import LOGIN_LOCKS, UserStatus
from app.results import FailureResult, ResultCode
from app.services import AuthenticationService
from app.utils import hash_password

from tests.factories import make_user

PASSWORD = "Str0ng!Pass1"


@pytest.fixture()
def service(db_session) -> AuthenticationService:
    return AuthenticationService(db_session)


def test_login_success(db_session, service):
    user = make_user(db_session, password=hash_password(PASSWORD))

    result = service.login(email=user.email, password=PASSWORD)

    assert result.success
    assert result.data.id == user.id


def test_login_with_incorrect_password_fails_and_counts_attempt(db_session, service):
    user = make_user(db_session, password=hash_password(PASSWORD))

    result = service.login(email=user.email, password="wrong-password")

    assert isinstance(result, FailureResult)
    assert user.failed_attempts == 1


def test_login_locks_account_after_threshold_failed_attempts(db_session, service):
    user = make_user(db_session, password=hash_password(PASSWORD))
    threshold = min(LOGIN_LOCKS.keys())

    for _ in range(threshold):
        service.login(email=user.email, password="wrong-password")

    assert user.failed_attempts == threshold
    assert user.lock_until is not None
    assert user.lock_until > datetime.now(UTC)

    # Even the CORRECT password must be rejected while locked.
    result = service.login(email=user.email, password=PASSWORD)

    assert isinstance(result, FailureResult)
    assert result.code == ResultCode.LOCKED


def test_login_blocked_user_cannot_authenticate(db_session, service):
    user = make_user(
        db_session, password=hash_password(PASSWORD), status=UserStatus.BLOCKED
    )

    result = service.login(email=user.email, password=PASSWORD)

    assert isinstance(result, FailureResult)
    assert result.code == ResultCode.LOCKED


def test_deleted_user_cannot_login(db_session, service):
    user = make_user(
        db_session, password=hash_password(PASSWORD), status=UserStatus.DELETED
    )

    result = service.login(email=user.email, password=PASSWORD)

    assert isinstance(result, FailureResult)
