# tests/api/test_conversation_members_routes.py

from app.utils import hash_password

from tests.factories import make_group, make_user

PASSWORD = "Str0ng!Pass1"


def test_non_member_cannot_list_conversation_members_via_api(client, db_session):
    alice = make_user(db_session, password=hash_password(PASSWORD))
    mallory = make_user(db_session, password=hash_password(PASSWORD))
    conversation = make_group(db_session, creator=alice)
    db_session.commit()

    signin = client.post(
        "/api/authentication/signin",
        json={"email": mallory.email, "password": PASSWORD},
    )
    assert signin.status_code == 200

    response = client.get(f"/api/conversations/{conversation.id}/members")

    assert response.status_code == 404
