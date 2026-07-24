# app/validators/users_validators.py

from email_validator import validate_email, EmailNotValidError
import phonenumbers
from phonenumbers import NumberParseException

from app.constants import (
    FIRST_NAME_MIN_LENGTH,
    FIRST_NAME_MAX_LENGTH,
    LAST_NAME_MIN_LENGTH,
    LAST_NAME_MAX_LENGTH,
    NAME_ALLOWED_SPECIAL_CHARACTERS,
    EMAIL_MAX_LENGTH,
    PASSWORD_MIN_LENGTH,
    PASSWORD_MAX_LENGTH,
    PASSWORD_SPECIAL_CHARACTERS
)


class RegisterValidator:

    @staticmethod
    def firstname(firstname: str | None) -> str | None:
        if not firstname:
            return "First name is required."

        firstname = firstname.strip()

        if not firstname:
            return "First name is required."

        length = len(firstname)

        if length < FIRST_NAME_MIN_LENGTH:
            return (
                f"First name must be at least {FIRST_NAME_MIN_LENGTH} characters long."
            )

        if length > FIRST_NAME_MAX_LENGTH:
            return f"First name cannot exceed {FIRST_NAME_MAX_LENGTH} characters."

        if not all(
            char.isalpha() or char in NAME_ALLOWED_SPECIAL_CHARACTERS
            for char in firstname
        ):
            return (
                "First name can only contain letters, spaces, apostrophes, and hyphens."
            )

        return None

    @staticmethod
    def lastname(lastname: str | None) -> str | None:
        if not lastname:
            return "Last name is required."

        lastname = lastname.strip()

        if not lastname:
            return "Last name is required."

        length = len(lastname)

        if length < LAST_NAME_MIN_LENGTH:
            return f"Last name must be at least {LAST_NAME_MIN_LENGTH} characters long."

        if length > LAST_NAME_MAX_LENGTH:
            return f"Last name cannot exceed {LAST_NAME_MAX_LENGTH} characters."

        if not all(
            char.isalpha() or char in NAME_ALLOWED_SPECIAL_CHARACTERS
            for char in lastname
        ):
            return (
                "Last name can only contain letters, spaces, apostrophes, and hyphens."
            )

        return None

    @staticmethod
    def email_address(email: str | None) -> str | None:
        if not email:
            return "Email is required."

        email = email.strip()

        if not email:
            return "Email is required."

        length = len(email)

        if length > EMAIL_MAX_LENGTH:
            return f"Email address cannot exceed {EMAIL_MAX_LENGTH} characters."

        try:
            validate_email(email, check_deliverability=False)
        except EmailNotValidError:
            return "Please enter a valid email address."

        return None

    @staticmethod
    def phone_number(phone_number: str | None) -> str | None:
        if not phone_number:
            return "Phone number is required."

        phone_number = phone_number.strip()

        if not phone_number:
            return "Phone number is required."

        try:
            parsed_number = phonenumbers.parse(phone_number)

            if not phonenumbers.is_valid_number(parsed_number):
                return "Please enter a valid phone number."

        except NumberParseException:
            return "Please enter a valid phone number."

        return None

    @staticmethod
    def password(password: str | None) -> str | None:
        if not password:
            return "Password is required."

        password = password.strip()

        if not password:
            return "Password is required."

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
            return f"Password must contain at least one special character."

        return None

    @staticmethod
    def confirm_password(password: str, confirm_password: str | None) -> str | None:
        if not confirm_password:
            return "Please confirm your password."

        confirm_password = confirm_password.strip()

        if not confirm_password:
            return "Please confirm your password."

        if confirm_password != password:
            return "Passwords do not match."

        return None
