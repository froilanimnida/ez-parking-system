""" This module contains the User class and UserOperations class. """
from sqlalchemy import Column, Integer, String, BINARY, VARCHAR, Enum, select, and_
from uuid import UUID
from sqlalchemy.exc import DataError, IntegrityError, OperationalError, DatabaseError

from app.exceptions.authorization_exception import IncorrectPasswordException
from app.utils.engine import get_session
from app.models.base import Base


class User(Base):
    """ Class to represent the user table in the database. """
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(BINARY(16), unique=True, nullable=False)
    username = Column(String(75), unique=True, nullable=False)
    first_name = Column(VARCHAR(100), nullable=False)
    last_name = Column(VARCHAR(100), nullable=False)
    email = Column(VARCHAR(75), unique=True, nullable=False)
    phone_number = Column(VARCHAR(15), unique=True, nullable=False)
    salt = Column(VARCHAR(45), nullable=False)
    hashed_password = Column(VARCHAR(255), nullable=False)
    role = Column(Enum('user', 'parking_manager', 'admin'),
                  nullable=False)
    

class UserOperations:
    """ Class to handle user operations, such as creating a new user or logging in a user. """
    @classmethod
    def create_new_user(cls, user_data: dict) -> str:  # pylint: disable=C0116
        session = get_session()
        try:
            new_user = User(
                uuid=user_data.get('uuid'),
                username=user_data.get('username'),
                first_name=user_data.get('first_name'),
                last_name=user_data.get('last_name'),
                email=user_data.get('email'),
                phone_number=user_data.get('phone_number'),
                salt=user_data.get('salt'),
                hashed_password=user_data.get('hashed_password'),
                role=user_data.get('role')
            )
            session.add(new_user)
            session.commit()
            # return the uuid but in readable format
            uuid = UUID(bytes=new_user.uuid)
            return str(uuid)
        except (DataError, IntegrityError, OperationalError, DatabaseError) as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    @classmethod
    def login_user(cls, login_data: dict) -> dict:  # pylint: disable=C0116
        session = get_session()
        try:
            user = session.execute(
                select(
                    User.id,
                    User.email, User.hashed_password, User.salt
                       ).where(
                    and_(
                        User.username == login_data.get('email'),
                        User.hashed_password == login_data.get('hashed_password'),
                    )
                )
            ).scalar()
            if user is None:
                raise IncorrectPasswordException('Incorrect password.')
            return {
                'id': user.id,
                'email': user.email,
                'hashed_password': user.hashed_password,
                'salt': user.salt
            }
        except (DataError, IntegrityError, OperationalError, DatabaseError) as e:
            session.rollback()
            raise e
        finally:
            session.close()
            
    @classmethod
    def is_email_taken(cls, email: str):
        session = get_session()
        try:
            user = session.execute(
                select(User).where(User.email == email)
            ).scalar()
            return user is not None
        except (DataError, IntegrityError, OperationalError, DatabaseError) as e:
            session.rollback()
            raise e
        finally:
            session.close()
    