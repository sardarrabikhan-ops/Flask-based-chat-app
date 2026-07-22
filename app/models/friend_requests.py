# app/models/friend_requests.py

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    String,
    DateTime,
    text,
    CheckConstraint,
    UniqueConstraint,
    ForeignKey,
)

from app.database import Base
from app.constants import FriendRequestStatus

if TYPE_CHECKING:
    from app.models.users import User


class FriendRequest(Base):

    __tablename__ = "friend_requests"

    allowed_status = ", ".join(f"'{status.value}'" for status in FriendRequestStatus)

    __table_args__ = (
        CheckConstraint(
            f"status IN ({allowed_status})", name="ck_friend_requests_status_valid"
        ),
        CheckConstraint(
            "sender_id <> receiver_id",
            name="ck_friend_requests_not_self",
        ),
        UniqueConstraint(
            "sender_id",
            "receiver_id",
            name="uq_friend_requests_sender_receiver",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    sender_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    receiver_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    status: Mapped[str] = mapped_column(
        String(15), default=FriendRequestStatus.PENDING.value, nullable=False
    )

    sender: Mapped["User"] = relationship(
        "User",
        back_populates="sent_friend_requests",
        foreign_keys=[sender_id],
    )

    receiver: Mapped["User"] = relationship(
        "User",
        back_populates="received_friend_requests",
        foreign_keys=[receiver_id],
    )
