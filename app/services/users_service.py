# app/services/users_service.py

from sqlalchemy.orm import Session

from app.models import User
from app.repositories import UserRepository

from app.utils import hash_password, format_phone_number, verify_password, format_time
from app.validators import RegisterValidator, LoginValidator

from app.constants import (
    UserStatus,
    LOGIN_LOCKS,
    MAX_LOGIN_ATTEMPTS,
    LOGIN_WARNING_THRESHOLD,
)
from app.schemas import ServiceResult

from datetime import datetime, UTC
from typing import Sequence


class UserService:
    """Provides user-related business logic."""

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
    ) -> ServiceResult[User]:
        """
        Register a new user.

        Returns:
            ServiceResult containing the created user or validation errors.
        """

        errors: dict[str, str] = {}

        # Validation
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
            return ServiceResult.fail(errors)

        # Tell the type checker these values are no longer None.
        assert firstname is not None
        assert lastname is not None
        assert email is not None
        assert phone_number is not None
        assert password is not None

        # normalizing fields
        firstname = firstname.strip()
        lastname = lastname.strip()
        email = email.strip().lower()
        phone_number = phone_number.strip()

        # Check uniqueness.
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
            return ServiceResult.fail(errors)

        # Format values for storage.
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

        return ServiceResult.ok(user)

    def login(self, email: str | None, password: str | None) -> ServiceResult[User]:
        """
        Authenticate a user.

        Returns:
            ServiceResult containing the authenticated user or login errors.
        """

        errors: dict[str, str] = {}

        # Validating fields
        if error := LoginValidator.email_address(email):
            errors["email"] = error

        if error := LoginValidator.password(password):
            errors["password"] = error

        if errors:
            return ServiceResult.fail(errors)

        # Tell the type checker these values are no longer None.
        assert email is not None
        assert password is not None

        # normalizing fields
        email = email.strip().lower()

        user = self.repository.get_by_email(email)

        # validating existence
        if user is None:
            errors["email"] = "Incorrect email or password."
            return ServiceResult.fail(errors)

        # validating status
        if user.status == UserStatus.BLOCKED:
            errors["account"] = "Your account has been blocked. Please contact support."
            return ServiceResult.fail(errors)

        # Verify account lock time.
        current_time = datetime.now(UTC)
        if user.lock_until and current_time < user.lock_until:
            free_time = format_time((user.lock_until - current_time).total_seconds())
            errors["account"] = (
                f"Your account is temporarily locked. Please try again after {free_time}."
            )
            return ServiceResult.fail(errors)

        # verifying password
        if not verify_password(password, user.password):

            user.failed_attempts += 1

            if user.failed_attempts in LOGIN_LOCKS:
                user.lock_until = current_time + LOGIN_LOCKS[user.failed_attempts]
                errors["account"] = (
                    f"Your account is locked for {format_time(LOGIN_LOCKS[user.failed_attempts].total_seconds())}!"
                )

            elif user.failed_attempts == MAX_LOGIN_ATTEMPTS:
                user.status = UserStatus.BLOCKED
                errors["account"] = (
                    "Your account has been blocked. Please contact support."
                )

            elif user.failed_attempts > LOGIN_WARNING_THRESHOLD:
                remaining = MAX_LOGIN_ATTEMPTS - user.failed_attempts
                errors["account"] = (
                    f"Warning: {remaining} login attempts remaining before your account is blocked."
                )

            errors["email"] = "Incorrect email or password."
            return ServiceResult.fail(errors)

        user.failed_attempts = 0
        user.lock_until = None

        return ServiceResult.ok(user)

    def get_all(
        self,
        status: UserStatus | None = UserStatus.ACTIVE,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ServiceResult[Sequence[User]]:
        """Return all users."""

        users = self.repository.get_all(
            status=status,
            limit=limit,
            offset=offset,
        )
        return ServiceResult.ok(users)

    def get_by_id(self, user_id: int | None) -> ServiceResult[User]:
        """Return the user with the given ID"""

        if user_id is None:
            return ServiceResult.fail({"user_id": "User ID is required."})

        user = self.repository.get_by_id(user_id)

        if user is None:
            return ServiceResult.fail({"user_id": "User not found."})

        return ServiceResult.ok(user)

    def search_by_name(
        self, name: str | None, limit: int | None = None, offset: int | None = None
    ) -> ServiceResult[Sequence[User]]:
        """Search the users with the given name"""

        if name is None:
            return ServiceResult.fail({"name": "name is required."})

        name = " ".join(name.split())

        if not name:
            return ServiceResult.fail({"name": "name is required."})

        users = self.repository.search_by_name(
            name, status=UserStatus.ACTIVE, limit=limit, offset=offset
        )

        if not users:
            return ServiceResult.fail({"name": "User not found."})

        return ServiceResult.ok(users)

    def get_by_email(self, email: str | None) -> ServiceResult[User]:
        """Return the user with the given email"""

        if error := LoginValidator.email_address(email):
            return ServiceResult.fail({"email": error})

        assert email is not None

        email = email.strip().lower()

        user = self.repository.get_by_email(email)

        if user is None:
            return ServiceResult.fail({"email": "User not found."})

        return ServiceResult.ok(user)

    def update_profile(
        self,
        user_id: int | None,
        firstname: str | None = None,
        lastname: str | None = None,
        phone_number: str | None = None,
    ) -> ServiceResult[User]:
        """
        Update a user's profile.

        Returns:
            ServiceResult containing the updated user or validation errors.
        """

        if user_id is None:
            return ServiceResult.fail({"user_id": "User ID is required."})

        user: User | None = self.repository.get_by_id(user_id)

        if user is None:
            return ServiceResult.fail({"user_id": "User not found."})

        errors: dict[str, str] = {}

        if firstname is not None:
            firstname = firstname.strip()

            if error := RegisterValidator.firstname(firstname):
                errors["firstname"] = error

            else:
                user.firstname = firstname

        if lastname is not None:
            lastname = lastname.strip()

            if error := RegisterValidator.lastname(lastname):
                errors["lastname"] = error

            else:
                user.lastname = lastname

        if phone_number is not None:
            phone_number = format_phone_number(phone_number)

            if error := RegisterValidator.phone_number(phone_number):
                errors["phone_number"] = error

            elif self.repository.exists_by_phone_number_except_user(
                user_id, phone_number
            ):
                errors["phone_number"] = "Phone number already exists."

            else:
                user.phone_number = phone_number

        if errors:
            return ServiceResult.fail(errors)

        return ServiceResult.ok(user)

    def change_password(
        self,
        user_id: int | None,
        current_password: str | None,
        new_password: str | None,
        confirm_password: str | None,
    ) -> ServiceResult[User]:
        """
        Update the user's password.

        Returns:
            ServiceResult containing the updated user or validation errors.
        """

        if user_id is None:
            return ServiceResult.fail({"user_id": "User ID is required."})

        user: User | None = self.repository.get_by_id(user_id)

        if user is None:
            return ServiceResult.fail({"user_id": "User not found."})

        errors: dict[str, str] = {}

        if error := LoginValidator.password(current_password):
            errors["current_password"] = error

        if error := LoginValidator.password(new_password):
            errors["new_password"] = error

        if errors:
            return ServiceResult.fail(errors)

        assert current_password is not None
        assert new_password is not None

        if error := RegisterValidator.confirm_password(new_password, confirm_password):
            errors["confirm_password"] = error

        if not verify_password(current_password, user.password):
            errors["current_password"] = "Current password is incorrect."

        if verify_password(new_password, user.password):
            errors["new_password"] = (
                "New password must be different from the current password."
            )

        if errors:
            return ServiceResult.fail(errors)

        user.password = hash_password(new_password)
        return ServiceResult.ok(user)

    def delete(self, user_id: int | None) -> ServiceResult[User]:
        """Soft-delete a user by marking its status as DELETED."""

        if user_id is None:
            return ServiceResult.fail({"user_id": "User ID is required."})

        user = self.repository.get_by_id(user_id)

        if user is None:
            return ServiceResult.fail({"user_id": "User not found."})

        user.status = UserStatus.DELETED

        return ServiceResult.ok(user)
