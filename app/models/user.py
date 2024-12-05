"""
    Represents a user in the database.

    Attributes:
        id (int): Primary key for the user.
        uuid (bytes): Unique identifier for the user.
        nickname (str): Optional nickname for the user.
        first_name (str): First name of the user.
        last_name (str): Last name of the user.
        email (str): Unique email address of the user.
        phone_number (str): Unique phone number of the user.
        role (Enum): Role of the user, can be 'user', 'parking_manager', or 'admin'.
        otp_secret (str): Optional one-time password secret.
        otp_expiry (datetime): Optional expiry time for the OTP.
        creation_date (datetime): Date when the user was created.
        parking_establishment (relationship): Relationship to the ParkingEstablishment model.
"""

# pylint: disable=R0801

from enum import Enum as PyEnum
from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    Column,
    Integer,
    Enum,
    select,
    update,
    CheckConstraint,
    UniqueConstraint,
    UUID,
    String,
    DateTime,
    Boolean,
)
from sqlalchemy.exc import DataError, IntegrityError, OperationalError, DatabaseError
from sqlalchemy.orm import relationship

from app.exceptions.authorization_exceptions import EmailNotFoundException, EmailAlreadyTaken, PhoneNumberAlreadyTaken
from app.models.audit import UUIDUtility
from app.models.base import Base
from app.routes.auth import AccountIsNotVerifiedException
from app.utils.db import session_scope
from app.utils.engine import get_session



class UserRole(PyEnum):
    user = 'user'
    parking_manager = 'parking_manager'
    admin = 'admin'

class User(Base):
    __tablename__ = 'user'
    
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(UUID(as_uuid=True), default=uuid4, unique=True, nullable=False)
    nickname = Column(String(24), nullable=True)
    first_name = Column(String(100), nullable=False)
    middle_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=False)
    suffix = Column(String(5), nullable=True)
    email = Column(String(75), nullable=False, unique=True)
    phone_number = Column(String(15), nullable=False, unique=True)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.user)
    plate_number = Column(String(10), nullable=True, unique=True)
    otp_secret = Column(String(6), nullable=True)
    otp_expiry = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    verification_token = Column(String(175), nullable=True)
    verification_expiry = Column(DateTime, nullable=True)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    __table_args__ = (
        UniqueConstraint('email', name='user_email_key'),
        UniqueConstraint('phone_number', name='user_phone_number_key'),
        UniqueConstraint('plate_number', name='user_plate_number_key'),
        UniqueConstraint('uuid', name='user_uuid_key'),
        CheckConstraint("role IN ('user', 'parking_manager', 'admin')", name="valid_role"),
    )
    parking_establishment = relationship(
        "ParkingEstablishment",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    banned_plate = relationship(
        "BannedPlate",
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="BannedPlate.plate_number",
    )
    audit = relationship(
        "Audit",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    files = relationship(
        "ParkingManagerFile", back_populates="manager", cascade="all, delete-orphan"
    )

    def to_dict(self):
        """Converts the user object to a dictionary."""
        uuid_utility = UUIDUtility()
        return {
            "user_id": self.user_id,
            "uuid": uuid_utility.format_uuid(uuid_utility.binary_to_uuid(self.uuid)),
            "nickname": self.nickname,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone_number": self.phone_number,
            "role": self.role,
            "plate_number": self.plate_number,
            "otp_secret": self.otp_secret,
            "otp_expiry": self.otp_expiry,
            "is_verified": self.is_verified,
            "verification_token": self.verification_token,
            "verification_expiry": self.verification_expiry,
            "created_at": self.created_at,
        }
    
class UserRepository:
    """Repository pattern for user operations"""
    
    @staticmethod
    def create_user(user_data: dict):
        """
        Creates a new user in the database with the provided user data.

        Parameters:
        user_data (dict): A dictionary containing user information.
                        Expected keys are 'uuid', 'first_name', 'last_name',
                        'email', 'phone_number', 'role', and 'creation_date'.

        Returns:
        int: The ID of the newly created user.

        Raises:
        DataError, IntegrityError, OperationalError, DatabaseError: If there is an error
        during the database operation, the session is rolled back and the exception is raised.
        """
        with session_scope() as session:
            new_user = User(
                first_name=user_data.get("first_name"),
                last_name=user_data.get("last_name"),
                nickname=user_data.get("nickname"),
                plate_number=user_data.get("plate_number"),
                email=user_data.get("email"),
                phone_number=user_data.get("phone_number"),
                role=user_data.get("role"),
                created_at=user_data.get("created_at"),
                verification_token=user_data.get("verification_token"),
                verification_expiry=user_data.get("verification_expiry"),
                is_verified=user_data.get("is_verified"),
            )
            session.add(new_user)
            return new_user.user_id
    
    
    @staticmethod
    def is_field_taken(field_name: str, value: str, exception):
        """
        Checks if a field value is already associated with an existing user.
    
        Parameters:
        field_name (str): The name of the field to check.
        value (str): The value to search for.
        exception: The exception to raise if the field is already taken.
    
        Raises:
        exception: If the field value already exists.
        """
        with session_scope() as session:
            filter_condition = {field_name: value}
            user = session.execute(select(User).filter_by(**filter_condition)).scalar()
            if user:
                raise exception(f"{field_name} already taken.")
            
    @staticmethod
    def verify_email(token: str):
        """
        Verify the email of a user identified by their token.

        Parameters:
        token (str): The token of the user whose email is to be verified.

        Raises:
        DataError, IntegrityError, OperationalError, DatabaseError: If there is an error
        during the database operation.
        """
        with session_scope() as session:
            session.execute(
                update(User)
                .where(User.verification_token == token)
                .values(
                    verification_token=None, verification_expiry=None, is_verified=True
                )
            )
    


class UserOperations:  # pylint: disable=R0903 disable=C0115

    @classmethod
    def create_new_user(cls, user_data: dict):
        """
        Creates a new user in the database with the provided user data.

        Parameters:
        user_data (dict): A dictionary containing user information.
                        Expected keys are 'uuid', 'first_name', 'last_name',
                        'email', 'phone_number', 'role', and 'creation_date'.

        Returns:
        int: The ID of the newly created user.

        Raises:
        DataError, IntegrityError, OperationalError, DatabaseError: If there is an error
        during the database operation, the session is rolled back and the exception is raised.
        """
        session = get_session()
        try:
            new_user = User(
                uuid=user_data.get("uuid"),
                first_name=user_data.get("first_name"),
                last_name=user_data.get("last_name"),
                nickname=user_data.get("nickname"),
                plate_number=user_data.get("plate_number"),
                email=user_data.get("email"),
                phone_number=user_data.get("phone_number"),
                role=user_data.get("role"),
                created_at=user_data.get("created_at"),
                verification_token=user_data.get("verification_token"),
                verification_expiry=user_data.get("verification_expiry"),
                is_verified=user_data.get("is_verified"),
            )
            session.add(new_user)
            session.commit()
            return new_user.user_id
        except (DataError, IntegrityError, OperationalError, DatabaseError) as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @classmethod
    def login_user(cls, email: str):
        """
        Authenticates a user by their email address.

        Parameters:
        email (str): The email address of the user attempting to log in.

        Returns:
        str: The email of the user if found.

        Raises:
        EmailNotFoundException: If the email is not found in the database.
        OperationalError, DatabaseError: If there is an error during the database operation.
        """
        session = get_session()
        try:
            user: User = session.execute(
                statement=select(User).where(User.email == email)
            ).scalar()
            if user is None:
                raise EmailNotFoundException("Email not found.")
            if user.is_verified is False:
                raise AccountIsNotVerifiedException("Account is not verified.")
            return user.email
        except (OperationalError, DatabaseError) as e:
            raise e
        finally:
            session.close()

    @classmethod
    def is_email_taken(cls, email: str) -> bool:
        """
        Checks if an email is already associated with an existing user.

        Parameters:
        email (str): The email address to check for existence.

        Returns:
        bool: True if the email is taken, False otherwise.

        Raises:
        DataError, IntegrityError, OperationalError, DatabaseError: If there is an error
        during the database operation.
        """
        session = get_session()
        try:
            user = session.execute(select(User).where(User.email == email)).scalar()
            return user is not None
        except (DataError, IntegrityError, OperationalError, DatabaseError) as e:
            raise e
        finally:
            session.close()

    @classmethod
    def is_phone_number_taken(cls, phone_number: str) -> bool:
        """
        Checks if a phone number is already associated with an existing user.

        Parameters:
        phone_number (str): The phone number to check for existence.

        Returns:
        bool: True if the phone number is taken, False otherwise.

        Raises:
        DataError, IntegrityError, OperationalError, DatabaseError: If there is an error
        during the database operation.
        """
        session = get_session()
        try:
            user = session.execute(
                select(User).where(User.phone_number == phone_number)
            ).scalar()
            return user is not None
        except (DataError, IntegrityError, OperationalError, DatabaseError) as e:
            raise e
        finally:
            session.close()

    @classmethod
    def verify_email(cls, token: str):
        """
        Verify the email of a user identified by their token.

        Parameters:
        token (str): The token of the user whose email is to be verified.

        Raises:
        DataError, IntegrityError, OperationalError, DatabaseError: If there is an error
        during the database operation.
        """
        session = get_session()
        try:
            session.execute(
                update(User)
                .where(User.verification_token == token)
                .values(
                    verification_token=None, verification_expiry=None, is_verified=True
                )
            )
            session.commit()
        except (DataError, IntegrityError, OperationalError, DatabaseError) as e:
            session.rollback()
            raise e
        finally:
            session.close()


class OTPOperations:
    """Class to handle operations related to OTP."""

    @classmethod
    def get_otp(cls, email: str):
        """
        Retrieve the OTP secret, expiry, user ID, and role for a given email.

        Args:
            email (str): The email address of the user.

        Returns:
            tuple: A tuple containing the OTP secret, OTP expiry, user ID, and role.

        Raises:
            EmailNotFoundException: If no user is found with the given email.
            DataError, IntegrityError, OperationalError, DatabaseError: If a database error occurs.
        """
        session = get_session()
        try:
            user = session.execute(
                select(
                    User.user_id,
                    User.otp_secret,
                    User.otp_expiry,
                    User.role,
                ).where(User.email == email)
            ).first()
            if user is None:
                raise EmailNotFoundException("Email not found.")
            user_id, otp_secret, otp_expiry, role = user
            return otp_secret, otp_expiry, user_id, role

        except (DataError, IntegrityError, OperationalError, DatabaseError) as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @classmethod
    def set_otp(cls, data: dict):
        """
        Update the OTP secret and expiry for a user identified by email.

        Args:
            data (dict): A dictionary containing the user's email, OTP secret,
                        and OTP expiry.

        Raises:
            DataError, IntegrityError, OperationalError, DatabaseError: If a
            database error occurs.
        """
        session = get_session()
        try:
            session.execute(
                update(User)
                .where(User.email == data.get("email"))
                .values(
                    otp_secret=data.get("otp_secret"), otp_expiry=data.get("otp_expiry")
                )
            )
            session.commit()
        except (DataError, IntegrityError, OperationalError, DatabaseError) as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @classmethod
    def delete_otp(cls, email: str):
        """
        Delete the OTP secret and expiry for a user identified by email.

        Args:
            email (str): The email address of the user.

        Raises:
            DataError, IntegrityError, OperationalError, DatabaseError: If a
            database error occurs.
        """
        session = get_session()
        try:
            session.execute(
                update(User)
                .where(User.email == email)
                .values(otp_secret=None, otp_expiry=None)
            )
            session.commit()
        except (DataError, IntegrityError, OperationalError, DatabaseError) as e:
            session.rollback()
            raise e
        finally:
            session.close()


class UserRepository:
    """Repository pattern for user operations"""

    @classmethod
    def get_by_plate_number(cls, plate_number: str) -> dict:
        """Get user by plate number"""
        return cls._execute_query(User.plate_number == plate_number)

    @classmethod
    def get_by_uuid(cls, uuid_bin: bytes) -> dict:
        """Get user by UUID"""
        return cls._execute_query(User.uuid == uuid_bin)

    @classmethod
    def get_by_id(cls, user_id: int) -> dict:
        """Get user by user_id"""
        return cls._execute_query(User.user_id == user_id)

    @classmethod
    def _execute_query(cls, filter_condition) -> dict:
        """Execute query"""
        session = get_session()
        try:
            user_info = session.execute(select(User).where(filter_condition)).scalar()
            return {} if user_info is None else user_info.to_dict()
        except (DataError, IntegrityError, OperationalError, DatabaseError) as e:
            raise e
        finally:
            session.close()
