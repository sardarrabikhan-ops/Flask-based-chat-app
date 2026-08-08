# tests/schemas/test_users_validators.py

from app.validators import RegisterValidator


def test_register_rejects_weak_password():
    error = RegisterValidator.password("weak")

    assert error is not None
