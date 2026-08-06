# app/models/users.py

from datetime import datetime, UTC
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, DateTime, text, CheckConstraint, Enum

from app.database import Base
from app.constants import (
    UserStatus,
    FIRST_NAME_MAX_LENGTH,
    LAST_NAME_MAX_LENGTH,
    EMAIL_MAX_LENGTH,
    PASSWORD_MAX_LENGTH,
    PHONE_NUMBER_LENGTH,
    MAX_LOGIN_ATTEMPTS,
)
from app.utils import get_enum_values

if TYPE_CHECKING:
    from app.models.conversation_members import ConversationMember
    from app.models.messages import Message
    from app.models.friend_requests import FriendRequest
    from app.models.friends import Friend


class User(Base):

    __tablename__ = "users"

    allowed_status = get_enum_values(UserStatus)

    __table_args__ = (
        CheckConstraint(
            f"failed_attempts BETWEEN 0 AND {MAX_LOGIN_ATTEMPTS}",
            name="ck_users_failed_attempts_range",
        ),
        CheckConstraint(
            f"status IN ({allowed_status})",
            name="ck_users_status_valid",
        ),
    )

    def __repr__(self) -> str:
        return f"User(id={self.id}, firstname={self.firstname}, lastname={self.lastname}, email={self.email}, phone_number={self.phone_number}, lock_until={self.lock_until}, failed_attempts={self.failed_attempts}, status={self.status}, created_at={self.created_at})"

    id: Mapped[int] = mapped_column(primary_key=True)

    firstname: Mapped[str] = mapped_column(
        String(FIRST_NAME_MAX_LENGTH), nullable=False
    )

    lastname: Mapped[str] = mapped_column(String(LAST_NAME_MAX_LENGTH), nullable=False)

    email: Mapped[str] = mapped_column(
        String(EMAIL_MAX_LENGTH), unique=True, nullable=False
    )

    phone_number: Mapped[str] = mapped_column(
        String(PHONE_NUMBER_LENGTH), unique=True, nullable=False
    )

    password: Mapped[str] = mapped_column(String(PASSWORD_MAX_LENGTH), nullable=False)

    failed_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    lock_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    updates_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=lambda: datetime.now(UTC),
    )

    status: Mapped[UserStatus] = mapped_column(
        Enum(
            UserStatus,
            values_callable=lambda enum: [e.value for e in enum],
            name="userstatus",
        ),
        nullable=False,
        default=UserStatus.ACTIVE,
    )

    conversation_members: Mapped[list["ConversationMember"]] = relationship(
        "ConversationMember", back_populates="user"
    )

    messages: Mapped[list["Message"]] = relationship("Message", back_populates="sender")

    sent_friend_requests: Mapped[list["FriendRequest"]] = relationship(
        "FriendRequest",
        foreign_keys="FriendRequest.sender_id",
        back_populates="sender",
    )

    received_friend_requests: Mapped[list["FriendRequest"]] = relationship(
        "FriendRequest",
        foreign_keys="FriendRequest.receiver_id",
        back_populates="receiver",
    )

    friendships: Mapped[list["Friend"]] = relationship(
        "Friend", foreign_keys="Friend.user_id", back_populates="user"
    )

    friendships_as_friend: Mapped[list["Friend"]] = relationship(
        "Friend", foreign_keys="Friend.friend_id", back_populates="friend"
    )
