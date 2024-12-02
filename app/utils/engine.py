"""
    This is responsible for initializing the Database engine and session
"""

from os import getenv
import logging
from logging import FileHandler, StreamHandler, getLogger
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

file_handler = FileHandler("authentication.logs")
file_handler.setLevel(logging.WARNING)

console_handler = StreamHandler()
console_handler.setLevel(logging.WARNING)

logger = getLogger()
logger.setLevel(logging.WARNING)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

IS_PRODUCTION = getenv("ENVIRONMENT") == "production"

DATABASE_URL = (
    IS_PRODUCTION and getenv("DATABASE_LIVE_URL") or getenv("DATABASE_DEV_URL")
)

engine = create_engine(DATABASE_URL)  # type: ignore

session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_engine():
    """Return the engine"""
    return engine


def get_session():
    """Returns the session"""
    return session_local()
