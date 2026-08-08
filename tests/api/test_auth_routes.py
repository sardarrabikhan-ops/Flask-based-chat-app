# tests/api/test_auth_routes.py

from app.constants import UserStatus
from app.models import User
from app.utils import hash_password

from tests.factories import make_user

PASSWORD = "Str0ng!Pass1"


def test_protected_endpoint_requires_authentication(client):
    response = client.get("/api/users/profile")

    assert response.status_code == 401


def test_delete_profile_clears_session_and_marks_user_deleted(client, db_session):
    user = make_user(db_session, password=hash_password(PASSWORD))
    user_id = user.id
    db_session.commit()

    signin = client.post(
        "/api/authentication/signin",
        json={"email": user.email, "password": PASSWORD},
    )
    assert signin.status_code == 200

    delete_response = client.delete("/api/users/profile")
    assert delete_response.status_code == 200

    db_session.expire_all()
    refreshed = db_session.get(User, user_id)
    assert refreshed.status == UserStatus.DELETED

    # A previously fixed bug let the stale session cookie keep working
    # after account deletion. Confirm it no longer authenticates.
    after_delete = client.get("/api/users/profile")
    assert after_delete.status_code == 401
