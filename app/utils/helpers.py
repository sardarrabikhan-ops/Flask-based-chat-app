# app/utils/helpers.py

from enum import Enum
import os
import phonenumbers
from datetime import timedelta

from app.constants import LOGIN_LOCKS


def require_env(name: str) -> str:
    value = os.getenv(name)

    if value is None:
        raise RuntimeError(f"Missing required environment variable: {name}")

    return value


def get_enum_values(enum_class: type[Enum]) -> str:
    return ", ".join(f"'{value.value}'" for value in enum_class)


def format_phone_number(phone_number: str) -> str:
    parsed = phonenumbers.parse(phone_number)

    return phonenumbers.format_number(
        parsed,
        phonenumbers.PhoneNumberFormat.E164,
    )


def is_plural(value: int) -> str:
    return "s" if value != 1 else ""


def format_time(seconds: float) -> str:
    seconds = int(seconds)

    if seconds == 0:
        return "0 seconds."

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60

    parts = []

    if hours:
        parts.append(f"{hours} hour{is_plural(hours)}")

    if minutes:
        parts.append(f"{minutes} minute{is_plural(minutes)}")

    if seconds:
        parts.append(f"{seconds} second{is_plural(seconds)}")

    return " ".join(parts) + "."


def escape_like(text: str) -> str:
    return text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def format_set(char_set: set[str]) -> str:
    items = sorted(char_set)

    if len(items) == 1:
        return items[0]

    return ", ".join(items[:-1]) + " and " + items[-1]


def get_lock_duration(failed_attempts: int) -> timedelta | None:

    lock_duration = None
    for attempts in sorted(LOGIN_LOCKS.keys(), reverse=True):
        if failed_attempts >= attempts:
            lock_duration = LOGIN_LOCKS[attempts]
            break

    return lock_duration
