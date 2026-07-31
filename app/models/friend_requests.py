# app/models/friend_requests.py

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    DateTime,
    text,
    CheckConstraint,
    UniqueConstraint,
    ForeignKey,
    Enum,
)

from app.database import Base
from app.constants import FriendRequestStatus
from app.utils import get_enum_values

if TYPE_CHECKING:
    from app.models.users import User


class FriendRequest(Base):

    __tablename__ = "friend_requests"

    allowed_status = get_enum_values(FriendRequestStatus)

    __table_args__ = (
        CheckConstraint(
            f"status IN ({allowed_status})", name="ck_friend_requests_status_valid"
        ),
        CheckConstraint(
            "sender_id <> receiver_id",
            name="ck_friend_requests_not_self",
        ),
    )

    def __repr__(self) -> str:
        return f"FriendRequest(id={self.id}, sender_id={self.sender_id}, receiver_id={self.receiver_id}, status={self.status}, created_at={self.created_at})"

    id: Mapped[int] = mapped_column(primary_key=True)

    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    receiver_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    status: Mapped[FriendRequestStatus] = mapped_column(
        Enum(
            FriendRequestStatus,
            values_callable=lambda enum: [e.value for e in enum],
            name="friendrequeststatus",
        ),
        nullable=False,
        default=FriendRequestStatus.PENDING,
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
