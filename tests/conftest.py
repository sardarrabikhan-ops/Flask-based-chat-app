# tests/conftest.py

from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env.test", override=True)

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import Config
from app.database import Base
from app import create_app


@pytest.fixture(scope="session")
def engine():
    """Dedicated test engine; schema is created once for the session.
    Tables are truncated (not dropped) up front so leftover rows from a
    previous run don't affect this one, without needing an
    ACCESS EXCLUSIVE lock at teardown that could hang waiting on the
    app's own separate connection pool (app/database.py's engine)."""
    test_engine = create_engine(Config.DB_URL)
    Base.metadata.create_all(test_engine)
    with test_engine.begin() as connection:
        for table in reversed(Base.metadata.sorted_tables):
            connection.execute(table.delete())
    yield test_engine
    test_engine.dispose()


@pytest.fixture(scope="session")
def flask_app(engine):
    """Build the Flask app once. Its own SessionLocal (app/database.py)
    points at the same DB_NAME set above, so it naturally talks to the
    same test database as `engine`/`db_session`."""
    application = create_app()
    application.config.update(TESTING=True)
    yield application

    # Release any connections the app's own engine/pool (app/database.py)
    # is still holding, so they can't block anything after the session.
    from app.database import engine as app_engine
    app_engine.dispose()


@pytest.fixture()
def db_session(engine):
    """A plain session for direct service-level tests and for setting up
    / asserting state around API-level tests. Truncates every table
    after each test so tests never leak state into each other."""
    session_factory = sessionmaker(bind=engine)
    session = session_factory()

    yield session

    session.rollback()
    session.close()

    with engine.begin() as connection:
        for table in reversed(Base.metadata.sorted_tables):
            connection.execute(table.delete())


@pytest.fixture()
def client(db_session, flask_app):
    """Flask test client for API-level tests. Data created via
    `db_session` must be committed (db_session.commit()) to be visible
    to requests made through this client, since they use separate DB
    connections."""
    return flask_app.test_client()
