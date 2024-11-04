""" This module contains the User class and UserOperations class. """
from sqlalchemy import DATETIME, Column, Integer, VARCHAR, BINARY, Enum, select, update
from sqlalchemy.exc import DataError, IntegrityError, OperationalError, DatabaseError
from sqlalchemy.orm.session import Session

from app.exceptions.authorization_exception import EmailNotFoundException

from app.utils.engine import get_session
from app.models.base import Base


class User(Base):  # pylint: disable=R0903
    """ Class to represent the user table in the database. """
    __tablename__: str = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(BINARY(length=16), unique=True, nullable=False)
    nickname = Column(VARCHAR(length=75), unique=True, nullable=True)
    first_name = Column(VARCHAR(length=100), nullable=False)
    last_name = Column(VARCHAR(length=100), nullable=False)
    email = Column(VARCHAR(length=75), unique=True, nullable=False)
    phone_number = Column(VARCHAR(length=15), unique=True, nullable=False)
    role = Column(Enum('user', 'parking_manager', 'admin'), nullable=False)
    otp_secret = Column(VARCHAR(length=10), nullable=True)
    otp_expiry = Column(DATETIME, nullable=True)
    creation_date = Column(DATETIME, nullable=False)


class UserOperations:
    """ Class to handle user operations, such as creating a new user or logging in a user. """
    @classmethod
    def create_new_user(cls, user_data: dict):  # pylint: disable=C0116
        session = get_session()
        try:
            new_user = User(
                uuid=user_data.get('uuid'),
                first_name=user_data.get('first_name'),
                last_name=user_data.get('last_name'),
                email=user_data.get('email'),
                phone_number=user_data.get('phone_number'),
                role=user_data.get('role'),
                creation_date=user_data.get('creation_date')
            )
            session.add(new_user)
            session.commit()
            return new_user.id
        except (DataError, IntegrityError, OperationalError, DatabaseError) as e:

            session.rollback()
            raise e
        finally:
            session.close()

    @classmethod
    def login_user(cls, email: str):  # pylint: disable=C0116
        session: Session = get_session()
        try:
            user: User = session.execute(
                statement=select(User).where(User.email == email)
            ).scalar()
            if user is None:
                raise EmailNotFoundException('Email not found.')
            return user.email
        except (OperationalError, DatabaseError) as e:
            raise e
        finally:
            session.close()

    @classmethod
    def is_email_taken(cls, email: str) -> bool:  # pylint: disable=C0116
        session: Session = get_session()
        try:
            user = session.execute(
                select(User).where(User.email == email)
            ).scalar()
            return user is not None
        except (DataError, IntegrityError, OperationalError, DatabaseError) as e:
            raise e
        finally:
            session.close()

    @classmethod
    def set_nickname(cls, email: str, nickname: str):  # pylint: disable=C0116
        session = get_session()
        try:
            session.execute(
                update(User).where(User.email == email).values(nickname=nickname)
            )
            session.commit()
        except (DataError, IntegrityError, OperationalError, DatabaseError) as e:
            session.rollback()
            raise e
        finally:
            session.close()


class OTPOperations:
    """ Class to handle operations related to OTP. """
    @classmethod
    def get_otp(cls, email: str):  # pylint: disable=C0116
        session: Session = get_session()
        try:
            user = session.execute(select(
                    User.id,
                    User.otp_secret,
                    User.otp_expiry
                )
                .where(User.email == email)
            ).first()
            if user is None:
                raise EmailNotFoundException('Email not found.')
            user_id, otp_secret, otp_expiry  = user
            return otp_secret, otp_expiry, user_id

        except (DataError, IntegrityError, OperationalError, DatabaseError) as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @classmethod
    def set_otp(cls, data: dict):  # pylint: disable=C0116
        session: Session = get_session()
        try:
            session.execute(
                update(User).where(
                    User.email == data.get('email')
                )
                .values(
                    otp_secret=data.get('otp_secret'),
                    otp_expiry=data.get('otp_expiry')
                )
            )
            session.commit()
        except (DataError, IntegrityError, OperationalError, DatabaseError) as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @classmethod
    def delete_otp(cls, email: str):  # pylint: disable=C0116
        session: Session = get_session()
        try:
            session.execute(
                update(User).where(User.email == email).values(
                    otp_secret=None,
                    otp_expiry=None
                )
            )
            session.commit()
        except (DataError, IntegrityError, OperationalError, DatabaseError) as e:
            session.rollback()
            raise e
        finally:
            session.close()
