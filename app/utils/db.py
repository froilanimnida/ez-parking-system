"""Provide a transactional scope around a series of operations."""

from contextlib import contextmanager
from sqlalchemy.exc import DataError, IntegrityError, OperationalError, DatabaseError
from app.utils.engine import get_session

@contextmanager
def session_scope():  # pylint: disable=C0116
    session = get_session()
    try:
        yield session
        session.commit()
    except (DataError, IntegrityError, OperationalError, DatabaseError) as e:
        session.rollback()
        raise e
    finally:
        session.close()
