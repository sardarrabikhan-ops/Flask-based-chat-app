# app/utils/helpers.py

from enum import Enum
import phonenumbers


def get_enum_values(enum_class: type[Enum]) -> str:
    return ", ".join(f"'{value.value}'" for value in enum_class)


def format_phone_number(phone_number: str) -> str:
    parsed = phonenumbers.parse(phone_number)

    phone_number = phonenumbers.format_number(
        parsed,
        phonenumbers.PhoneNumberFormat.E164,
    )

    return phone_number


def format_time(seconds: float) -> str:
    seconds = int(seconds)

    if seconds < 60:
        return f"{seconds} second(s)."

    if seconds < 3600:
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes} minute(s) {seconds} second(s)."

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{hours} hour(s) {minutes} minute(s) {seconds} second(s)."


def escape_like(text: str) -> str:
    return text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def format_set(char_set: set) -> str:
    lst = list(char_set)
    return ", ".join(lst[:-1]) + " and " + lst[-1]
