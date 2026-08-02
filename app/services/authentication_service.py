# app/services/authentication_service.py

from app.models import User
from app.services import BaseService

from app.schemas import ServiceResult
from app.utils import format_phone_number, format_time, hash_password, verify_password

from app.validators import RegisterValidator, LoginValidator
from app.constants import (
    UserStatus,
    LOGIN_LOCKS,
    MAX_LOGIN_ATTEMPTS,
)

from datetime import UTC, datetime


class AuthenticationService(BaseService):
    """Provides authentication service."""

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

        validation_errors = self._validate_register_inputs(
            firstname, lastname, email, phone_number, password
        )

        if validation_errors:
            return ServiceResult.fail(validation_errors)

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
        phone_number = format_phone_number(phone_number.strip())

        # Check uniqueness.
        if error := RegisterValidator.confirm_password(password, confirm_password):
            errors["confirm_password"] = error

        user = self.user_repository.get_by_email(email, deleted=True)

        if user is not None and user.status != UserStatus.DELETED:
            errors["email"] = (
                "An account with this email already exists. Please sign in or use a different email address."
            )

        phone_user = self.user_repository.get_by_phone_number(phone_number)

        if phone_user is not None:
            if user is None or phone_user.id != user.id:
                errors["phone_number"] = (
                    "An account with this phone number already exists. Please sign in or use a different phone number."
                )

        if errors:
            return ServiceResult.fail(errors)

        if user is not None:
            self._restore_deleted_user(
                user, firstname, lastname, phone_number, password
            )
            return ServiceResult.ok(user)

        # Format values for storage.
        password = hash_password(password)

        user = User(
            firstname=firstname,
            lastname=lastname,
            email=email,
            phone_number=phone_number,
            password=password,
        )

        user = self.user_repository.create(user)

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

        user = self.user_repository.get_by_email(email)

        # validating existence
        if user is None:
            return ServiceResult.fail({"email": "Incorrect email or password."})

        # validating status
        if user.status == UserStatus.BLOCKED:
            return ServiceResult.fail(
                {"account": "Your account has been blocked. Please contact support."}
            )

        # Verify account lock time.
        current_time = datetime.now(UTC)
        if user.lock_until and current_time < user.lock_until:
            free_time = format_time((user.lock_until - current_time).total_seconds())
            return ServiceResult.fail(
                {
                    "account": f"Your account is temporarily locked. Please try again after {free_time}."
                }
            )

        # verifying password
        if not verify_password(password, user.password):

            user.failed_attempts += 1

            if user.failed_attempts >= MAX_LOGIN_ATTEMPTS:
                user.status = UserStatus.BLOCKED
                errors["account"] = (
                    "Your account has been blocked. Please contact support."
                )

            else:

                lock_duration = None
                for attempts in sorted(LOGIN_LOCKS.keys(), reverse=True):
                    if user.failed_attempts >= attempts:
                        lock_duration = LOGIN_LOCKS[attempts]
                        break

                if lock_duration is not None:
                    user.lock_until = current_time + lock_duration
                    errors["account"] = (
                        f"Your account is locked for {format_time(lock_duration.total_seconds())}!"
                    )

            errors["email"] = "Incorrect email or password."
            return ServiceResult.fail(errors)

        user.failed_attempts = 0
        user.lock_until = None

        return ServiceResult.ok(user)
