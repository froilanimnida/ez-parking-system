"""
    This is responsible for initializing the Database engine and session
"""

import logging
from logging import FileHandler, StreamHandler, getLogger
from os import getenv

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

file_handler = FileHandler("authentication.logs")
file_handler.setLevel(logging.WARNING)

console_handler = StreamHandler()
console_handler.setLevel(logging.WARNING)

logger = getLogger()
logger.setLevel(logging.WARNING)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

engine = create_engine(
    getenv("DATABASE_URL"),
    echo=True,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,
)

@event.listens_for(engine, 'connect')
def receive_connect(dbapi_connection, connection_record):
    print('Connection established:', connection_record)

@event.listens_for(engine, 'checkout')
def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    print('Connection checkout:', connection_record)

session_local = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)

# ...existing code...

def get_engine():
    """Return the engine"""
    return engine


def get_session():
    """Returns the session"""
    return session_local()
