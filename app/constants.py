# app/constants.py

from enum import Enum
from datetime import timedelta


class UserStatus(Enum):
    ACTIVE = "active"
    DELETED = "deleted"
    BLOCKED = "blocked"


class ConversationType(Enum):
    PRIVATE = "private"
    GROUP = "group"


class ConversationMemberRole(Enum):
    ADMIN = "admin"
    MEMBER = "member"


class ConversationMemberStatus(Enum):
    ACTIVE = "active"
    LEFT = "left"
    REMOVED = "removed"


class MessageStatus(Enum):
    ACTIVE = "active"
    DELETED = "deleted"


class MessageDeliveryStatus(Enum):
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"


class FriendStatus(Enum):
    ACTIVE = "active"
    REMOVED = "removed"


class FriendRequestStatus(Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CANCELED = "canceled"


FIRST_NAME_MIN_LENGTH: int = 2
FIRST_NAME_MAX_LENGTH: int = 50

LAST_NAME_MIN_LENGTH: int = 2
LAST_NAME_MAX_LENGTH: int = 50

EMAIL_MAX_LENGTH: int = 255

PASSWORD_MIN_LENGTH: int = 8
PASSWORD_MAX_LENGTH: int = 255

PHONE_NUMBER_LENGTH: int = 16

NAME_ALLOWED_SPECIAL_CHARACTERS: set[str] = {"-", "'", " "}
CONVERSATION_NAME_ALLOWED_SPECIAL_CHARACTERS: set[str] = {
    "-",
    "'",
    "_",
    ".",
    "/",
    ";",
    ":",
}

PASSWORD_SPECIAL_CHARACTERS: str = "!@#$%&()_><?/"

LOGIN_LOCKS: dict[int, timedelta] = {
    3: timedelta(seconds=30),
    5: timedelta(minutes=5),
    7: timedelta(minutes=15),
    10: timedelta(minutes=30),
    12: timedelta(minutes=45),
    15: timedelta(hours=1),
    18: timedelta(hours=1.5),
    19: timedelta(hours=3),
}

MAX_LOGIN_ATTEMPTS: int = 20

CONVERSATION_NAME_MAX_LENGTH = 60
CONVERSATION_NAME_MIN_LENGTH = 3

MESSAGE_MAX_LENGTH = 10000
