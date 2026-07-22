# app/models/users.py

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, DateTime, text, CheckConstraint

from app.database import Base
from app.constants import UserStatus

if TYPE_CHECKING:
    from app.models.conversation_members import ConversationMember
    from app.models.messages import Message
    from app.models.friend_requests import FriendRequest
    from app.models.friends import Friend


class User(Base):

    __tablename__ = "users"

    allowed_status = ", ".join(f"'{status.value}'" for status in UserStatus)

    __table_args__ = (
        CheckConstraint(
            "failed_attempts BETWEEN 0 AND 15",
            name="ck_users_failed_attempts_range",
        ),
        CheckConstraint(
            f"status IN ({allowed_status})",
            name="ck_users_status_valid",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    firstname: Mapped[str] = mapped_column(String(15), nullable=False)

    lastname: Mapped[str] = mapped_column(String(15), nullable=False)

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    phone_number: Mapped[str] = mapped_column(String(13), unique=True, nullable=False)

    password: Mapped[str] = mapped_column(String(255), nullable=False)

    failed_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    lock_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    status: Mapped[str] = mapped_column(
        String(15), nullable=False, default=UserStatus.ACTIVE.value
    )

    conversation_members: Mapped[list["ConversationMember"]] = relationship(
        "ConversationMember", back_populates="user", cascade="all, delete-orphan"
    )

    messages: Mapped[list["Message"]] = relationship("Message", back_populates="sender")

    sent_friend_requests: Mapped[list["FriendRequest"]] = relationship(
        "FriendRequest",
        foreign_keys="FriendRequest.sender_id",
        back_populates="sender",
        cascade="all, delete-orphan",
    )

    received_friend_requests: Mapped[list["FriendRequest"]] = relationship(
        "FriendRequest",
        foreign_keys="FriendRequest.receiver_id",
        back_populates="receiver",
        cascade="all, delete-orphan",
    )

    friendships: Mapped[list["Friend"]] = relationship(
        "Friend", foreign_keys="Friend.user_id", back_populates="user"
    )

    friendships_as_friend: Mapped[list["Friend"]] = relationship(
        "Friend", foreign_keys="Friend.friend_id", back_populates="friend"
    )
