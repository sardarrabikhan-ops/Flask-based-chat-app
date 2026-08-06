# app/lifecycle.py

from flask import g, session

from sqlalchemy.orm import Session
from app.database import SessionLocal

from app.constants import SESSION_USER_ID
from app.dependencies import Dependencies
from app.results import SuccessResult


def before_request() -> None:

    deps = Dependencies()

    g.db = SessionLocal()

    user_id = session.get(SESSION_USER_ID)

    if user_id is None:
        g.user = None
        return

    result = deps.user_service.get_by_id(user_id)

    if isinstance(result, SuccessResult):
        g.user = result.data
    else:
        g.user = None


def teardown_request(exception: BaseException | None) -> None:

    db: Session | None = getattr(g, "db", None)

    if db is None:
        return

    try:
        if exception is None:
            db.commit()
        else:
            db.rollback()

    finally:
        db.close()
