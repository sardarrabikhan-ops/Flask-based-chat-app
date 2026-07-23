# app/utils/helpers.py

from enum import Enum


def get_enum_values(enum_class: type[Enum]) -> str:
    return ", ".join(f"'{value.value}'" for value in enum_class)
