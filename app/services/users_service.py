# app/services/users_service.py

from app.models import User
from app.services import BaseService

from app.utils import hash_password, format_phone_number, verify_password
from app.validators import RegisterValidator, LoginValidator

from app.constants import (
    UserStatus,
    FriendStatus,
)
from app.schemas import ServiceResult

from typing import Sequence


class UserService(BaseService):
    """Provides user-related business logic."""

    def get_all(
        self,
        status: UserStatus | None = UserStatus.ACTIVE,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ServiceResult[Sequence[User]]:
        """Return all users."""

        users = self.user_repository.get_all(
            status=status, limit=limit, offset=offset, order_by=User.created_at.asc()
        )

        return ServiceResult.ok(users)

    def get_by_id(self, user_id: int | None) -> ServiceResult[User]:
        """Return the user with the given ID"""

        return self._require_user(user_id)

    def search_by_name(
        self, name: str | None, limit: int | None = None, offset: int | None = None
    ) -> ServiceResult[Sequence[User]]:
        """Search the users with the given name"""

        if name is None:
            return ServiceResult.fail({"name": "name is required."})

        name = " ".join(name.split())

        if not name:
            return ServiceResult.fail({"name": "name is required."})

        users = self.user_repository.search_by_name(
            name, status=UserStatus.ACTIVE, limit=limit, offset=offset
        )

        return ServiceResult.ok(users)

    def get_by_email(self, email: str | None) -> ServiceResult[User]:
        """Return the user with the given email"""

        if error := LoginValidator.email_address(email):
            return ServiceResult.fail({"email": error})

        assert email is not None

        email = email.strip().lower()

        user = self.user_repository.get_by_email(email)

        if user is None:
            return ServiceResult.fail({"email": "User not found."})

        if user.status == UserStatus.BLOCKED:
            return ServiceResult.fail({"email": "User is blocked."})

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

        result = self._require_user(user_id)

        if not result.success:
            return result

        assert user_id is not None
        assert result.data is not None

        user = result.data

        errors: dict[str, str] = {}

        if firstname is not None:
            firstname = firstname.strip()

            if error := RegisterValidator.firstname(firstname):
                errors["firstname"] = error

        if lastname is not None:
            lastname = lastname.strip()

            if error := RegisterValidator.lastname(lastname):
                errors["lastname"] = error

        if phone_number is not None:
            phone_number = format_phone_number(phone_number.strip())

            if error := RegisterValidator.phone_number(phone_number):
                errors["phone_number"] = error

            elif (
                user.phone_number != phone_number
                and self.user_repository.exists_by_phone_number_except_user(
                    user_id, phone_number
                )
            ):
                errors["phone_number"] = "Phone number already exists."

        if errors:
            return ServiceResult.fail(errors)

        if firstname is not None and user.firstname != firstname:
            user.firstname = firstname

        if lastname is not None and user.lastname != lastname:
            user.lastname = lastname

        if phone_number is not None and user.phone_number != phone_number:
            user.phone_number = phone_number

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

        result = self._require_user(user_id)

        if not result.success:
            return result

        assert user_id is not None
        assert result.data is not None

        user = result.data

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

        if errors:
            return ServiceResult.fail(errors)

        if verify_password(new_password, user.password):
            return ServiceResult.fail(
                {
                    "new_password": "New password must be different from the current password."
                }
            )

        user.password = hash_password(new_password)
        return ServiceResult.ok(user)

    def delete(self, user_id: int | None) -> ServiceResult[User]:
        """Soft-delete a user by marking its status as DELETED."""

        result = self._require_user(user_id)

        if not result.success:
            return result

        assert user_id is not None
        assert result.data is not None

        user = result.data

        user.status = UserStatus.DELETED

        for membership in user.conversation_members:
            membership.is_hidden = True

        friendships = self.friend_repository.get_by_user_id(user_id)

        for friendship in friendships:
            friendship.status = FriendStatus.REMOVED

        return ServiceResult.ok(user)
