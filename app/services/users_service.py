# app/services/users_service.py

from sqlalchemy.orm import Session

from app.models import User
from app.repositories import UserRepository

from app.utils import hash_password, format_phone_number, verify_password, format_time
from app.validators import RegisterValidator

from app.constants import (
    UserStatus,
    LOGIN_LOCKS,
    MAX_LOGIN_ATTEMPTS,
    LOGIN_WARNING_THRESHOLD,
)

from datetime import datetime, UTC


class UserService:

    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = UserRepository(self.session)

    def register(
        self,
        firstname: str | None,
        lastname: str | None,
        email: str | None,
        phone_number: str | None,
        password: str | None,
        confirm_password: str | None,
    ) -> dict[str, bool | dict | User]:

        errors = {}

        if error := RegisterValidator.firstname(firstname):
            errors["firstname"] = error

        if error := RegisterValidator.lastname(lastname):
            errors["lastname"] = error

        if error := RegisterValidator.email_address(email):
            errors["email"] = error

        if error := RegisterValidator.phone_number(phone_number):
            errors["phone_number"] = error

        if error := RegisterValidator.password(password):
            errors["password"] = error

        if errors:
            return {"success": False, "errors": errors}

        assert firstname is not None
        assert lastname is not None
        assert email is not None
        assert phone_number is not None
        assert password is not None

        firstname = firstname.strip()
        lastname = lastname.strip()
        email = email.strip().lower()
        phone_number = phone_number.strip()

        if error := RegisterValidator.confirm_password(password, confirm_password):
            errors["confirm_password"] = error

        if self.repository.exists_by_email(email):
            errors["email"] = (
                "An account with this email already exists. Please sign in or use a different email address."
            )

        if self.repository.exists_by_phone_number(phone_number):
            errors["phone_number"] = (
                "An account with this phone number already exists. Please sign in or use a different phone number."
            )

        if errors:
            return {"success": False, "errors": errors}

        password = hash_password(password)
        phone_number = format_phone_number(phone_number)

        user = User(
            firstname=firstname,
            lastname=lastname,
            email=email,
            phone_number=phone_number,
            password=password,
        )

        user = self.repository.create(user)

        return {"success": True, "data": user}

    def login(
        self, email: str | None, password: str | None
    ) -> dict[str, bool | dict | User]:

        errors = {}

        if not email or not email.strip():
            errors["email"] = "Email is required."

        if not password or not password.strip():
            errors["password"] = "Password is required."

        if errors:
            return {"success": False, "errors": errors}

        assert email is not None
        assert password is not None

        email = email.strip().lower()

        user = self.repository.get_by_email(email)

        if user is None:
            errors["email"] = "Incorrect email or password."
            return {"success": False, "errors": errors}

        if user.status == UserStatus.BLOCKED:
            errors["status"] = "Your account has been blocked. Please contact support."
            return {"success": False, "errors": errors}

        current_time = datetime.now(UTC)
        if user.lock_until and current_time < user.lock_until:
            free_time = format_time((user.lock_until - current_time).total_seconds())
            errors["lock_until"] = (
                f"Your account is temporarily locked. Please try again after {free_time}."
            )
            return {"success": False, "errors": errors}

        if not verify_password(password, user.password):

            user.failed_attempts += 1

            if user.failed_attempts in LOGIN_LOCKS:
                user.lock_until = current_time + LOGIN_LOCKS[user.failed_attempts]
                errors["locked"] = (
                    f"Account is locked for {format_time(LOGIN_LOCKS[user.failed_attempts].total_seconds())}!"
                )

            elif user.failed_attempts == MAX_LOGIN_ATTEMPTS:
                user.status = UserStatus.BLOCKED
                errors["status"] = (
                    "Your account has been blocked. Please contact support."
                )

            elif user.failed_attempts > LOGIN_WARNING_THRESHOLD:
                errors["locked"] = (
                    "Warning: Too many failed login attempts. Your account will be blocked after 15 failed attempts."
                )

            errors["email"] = "Incorrect email or password."
            return {"success": False, "errors": errors}

        user.failed_attempts = 0
        user.lock_until = None
        return {"success": True, "data": user}
