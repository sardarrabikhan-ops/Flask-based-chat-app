# app/models/users.py

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime, text, CheckConstraint

from datetime import datetime
from app.database import Base
from app.constants import UserStatus


class User(Base):

    __tablename__ = "users"

    allowed = ", ".join(f"'{status.value}'" for status in UserStatus)

    __table_args__ = (
        CheckConstraint(
            "failed_attempts BETWEEN 0 AND 15",
            name="ck_users_failed_attempts_range",
        ),
        CheckConstraint(
            f"status IN ({allowed})",
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
