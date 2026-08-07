# app/validators/users_validators.py

from email_validator import validate_email, EmailNotValidError
import phonenumbers
from phonenumbers import NumberParseException

from app.validators import BaseValidator
from app.constants import (
    FIRST_NAME_MIN_LENGTH,
    FIRST_NAME_MAX_LENGTH,
    LAST_NAME_MIN_LENGTH,
    LAST_NAME_MAX_LENGTH,
    NAME_ALLOWED_SPECIAL_CHARACTERS,
    EMAIL_MAX_LENGTH,
    PASSWORD_MIN_LENGTH,
    PASSWORD_MAX_LENGTH,
    PASSWORD_SPECIAL_CHARACTERS,
)


class RegisterValidator(BaseValidator):

    @staticmethod
    def firstname(firstname: str | None) -> str | None:
        return RegisterValidator._validate_name(
            firstname,
            "First name",
            FIRST_NAME_MIN_LENGTH,
            FIRST_NAME_MAX_LENGTH,
            NAME_ALLOWED_SPECIAL_CHARACTERS,
        )

    @staticmethod
    def lastname(lastname: str | None) -> str | None:
        return RegisterValidator._validate_name(
            lastname,
            "Last name",
            LAST_NAME_MIN_LENGTH,
            LAST_NAME_MAX_LENGTH,
            NAME_ALLOWED_SPECIAL_CHARACTERS,
        )

    @staticmethod
    def email_address(email: str | None) -> str | None:
        if error := RegisterValidator._validate_string(email, "Email"):
            return error

        assert email is not None

        if len(email) > EMAIL_MAX_LENGTH:
            return f"Email address cannot exceed {EMAIL_MAX_LENGTH} characters."

        try:
            validate_email(email, check_deliverability=False)
        except EmailNotValidError:
            return "Please enter a valid email address."

        return None

    @staticmethod
    def phone_number(phone_number: str | None) -> str | None:
        if error := RegisterValidator._validate_string(phone_number, "Phone number"):
            return error

        assert phone_number is not None

        try:
            parsed_number = phonenumbers.parse(phone_number)

            if not phonenumbers.is_valid_number(parsed_number):
                return "Please enter a valid phone number in international format (e.g. +92XXXXXXXXXX)."

        except NumberParseException:
            return "Please enter a valid phone number in international format (e.g. +92XXXXXXXXXX)."

        return None

    @staticmethod
    def password(password: str | None) -> str | None:
        if error := RegisterValidator._validate_string(password, "Password"):
            return error

        assert password is not None

        length = len(password)

        if length < PASSWORD_MIN_LENGTH:
            return f"Password must be at least {PASSWORD_MIN_LENGTH} characters long."

        if length > PASSWORD_MAX_LENGTH:
            return f"Password cannot exceed {PASSWORD_MAX_LENGTH} characters."

        if not any(char.isupper() for char in password):
            return "Password must contain at least one uppercase letter."

        if not any(char.islower() for char in password):
            return "Password must contain at least one lowercase letter."

        if not any(char.isdigit() for char in password):
            return "Password must contain at least one digit."

        if not any(char in PASSWORD_SPECIAL_CHARACTERS for char in password):
            return "Password must contain at least one special character."

        return None

    @staticmethod
    def confirm_password(password: str, confirm_password: str | None) -> str | None:
        if error := RegisterValidator._validate_string(
            confirm_password, "Confirm password"
        ):
            return error

        if confirm_password != password:
            return "Passwords do not match."

        return None


class LoginValidator(BaseValidator):

    @staticmethod
    def email_address(email: str | None) -> str | None:
        return LoginValidator._validate_string(email, "Email")

    @staticmethod
    def password(password: str | None) -> str | None:
        return LoginValidator._validate_string(password, "Password")
