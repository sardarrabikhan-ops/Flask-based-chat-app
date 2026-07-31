# app/models/friends.py

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, text, CheckConstraint, ForeignKey, Enum

from app.database import Base
from app.constants import FriendStatus
from app.utils import get_enum_values

if TYPE_CHECKING:
    from app.models.users import User


class Friend(Base):

    __tablename__ = "friends"

    allowed_status = get_enum_values(FriendStatus)

    __table_args__ = (
        CheckConstraint(
            f"status IN ({allowed_status})", name="ck_friends_status_valid"
        ),
        CheckConstraint(
            "user_id < friend_id", name="ck_friends_user_id_less_than_friend_id"
        ),
    )

    def __repr__(self) -> str:
        return f"Friend(user_id={self.user_id}, friend_id={self.friend_id}, status={self.status}, created_at={self.created_at})"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)

    friend_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    status: Mapped[FriendStatus] = mapped_column(
        Enum(
            FriendStatus,
            values_callable=lambda enum: [e.value for e in enum],
            name="friendstatus",
        ),
        nullable=False,
        default=FriendStatus.ACTIVE,
    )

    user: Mapped["User"] = relationship(
        "User", back_populates="friendships", foreign_keys=[user_id]
    )

    friend: Mapped["User"] = relationship(
        "User", back_populates="friendships_as_friend", foreign_keys=[friend_id]
    )
