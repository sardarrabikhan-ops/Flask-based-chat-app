# app/constants.py

from enum import Enum


class UserStatus(Enum):
    ACTIVE = "active"
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
    ACTIVE = "active"
    DELETED = "deleted"


class ConversationMemberRole(Enum):
    ADMIN = "admin"
    MEMBER = "member"
