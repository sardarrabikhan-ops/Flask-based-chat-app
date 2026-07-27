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


class ConversationStatus(Enum):
    ACTIVE = "active"
    DELETED = "deleted"
    ARCHIVED = "archived"


class FriendRequestStatus(Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class FriendStatus(Enum):
    ACTIVE = "active"
    REMOVED = "removed"


class MessageStatus(Enum):
    SENT = "sent"
    DELIEVERED = "delievered"
    READ = "read"
    ACTIVE = "active"
    DELETED = "deleted"


class ConversationMemberRole(Enum):
    ADMIN = "admin"
    MEMBER = "member"


FIRST_NAME_MIN_LENGTH: int = 2
FIRST_NAME_MAX_LENGTH: int = 50

LAST_NAME_MIN_LENGTH: int = 2
LAST_NAME_MAX_LENGTH: int = 50

EMAIL_MAX_LENGTH: int = 255

PASSWORD_MIN_LENGTH: int = 8
PASSWORD_MAX_LENGTH: int = 255

PHONE_NUMBER_LENGTH: int = 16

NAME_ALLOWED_SPECIAL_CHARACTERS: set = {"-", "'", " "}

PASSWORD_SPECIAL_CHARACTERS: str = "!@#$%&()_><?/"

LOGIN_LOCKS: dict = {
    3: timedelta(seconds=30),
    5: timedelta(minutes=5),
    7: timedelta(minutes=15),
    10: timedelta(minutes=30),
    12: timedelta(minutes=45),
    15: timedelta(hours=1),
    18: timedelta(hours=1.5),
    19: timedelta(hours=3),
}

LOGIN_WARNING_THRESHOLD = 7

MAX_LOGIN_ATTEMPTS: int = 20

CONVERSATION_NAME_MAX_LENGTH = 30
CONVERSATION_NAME_MIN_LENGTH = 3