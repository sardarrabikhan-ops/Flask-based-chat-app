# tests/services/test_messages_service.py

import pytest

from app.results import FailureResult
from app.services import ConversationService

from tests.factories import make_user


@pytest.fixture()
def service(db_session) -> ConversationService:
    return ConversationService(db_session)


def test_create_group(db_session, service):
    alice = make_user(db_session)
    result = service.create_group(alice.id, name="My Group")

    assert result is not None
    assert not isinstance(result, FailureResult)
    assert result.success
    assert result.data.id is not None
    assert result.data.name == "My Group"
