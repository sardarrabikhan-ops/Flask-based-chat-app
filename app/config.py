# app/config.py

from app.utils import require_env
from dotenv import load_dotenv
import os

load_dotenv()


class Config:

    DB_USER = require_env("DB_USER")
    DB_PASSWORD = require_env("DB_PASSWORD")
    DB_PORT = require_env("DB_PORT")
    DB_HOST = require_env("DB_HOST")
    DB_NAME = require_env("DB_NAME")

    DB_URL = (
        f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    SECRET_KEY = require_env("SECRET_KEY")

    DEBUG = os.getenv("DEBUG", "").lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
