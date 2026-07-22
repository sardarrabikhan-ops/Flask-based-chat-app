# app/models/friends.py

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, text, CheckConstraint, ForeignKey

from app.database import Base
from app.constants import FriendStatus

if TYPE_CHECKING:
    from app.models.users import User


class Friend(Base):

    __tablename__ = "friends"

    allowed_status = ", ".join(f"'{status.value}'" for status in FriendStatus)

    __table_args__ = (
        CheckConstraint(
            f"status IN ({allowed_status})", name="ck_friends_status_valid"
        ),
        CheckConstraint(
            "user_id < friend_id", name="ck_friends_user_id_less_than_friend_id"
        ),
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )

    friend_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    status: Mapped[str] = mapped_column(
        String(15), default=FriendStatus.ACTIVE.value, nullable=False
    )

    user: Mapped["User"] = relationship(
        "User", back_populates="friendships", foreign_keys=[user_id]
    )

    friend: Mapped["User"] = relationship(
        "User", back_populates="friendships_as_friend", foreign_keys=[friend_id]
    )
