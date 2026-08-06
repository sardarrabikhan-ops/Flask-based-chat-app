# database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.config import Config

engine = create_engine(Config.DB_URL, pool_pre_ping=True)

SessionLocal: sessionmaker = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass
