"""
    Represents a user in the database.
"""

# pylint: disable=R0801, C0103

from enum import Enum as PyEnum
from typing import overload
from uuid import uuid4

from sqlalchemy import (
    Column, Integer, Enum, select, update, CheckConstraint, UniqueConstraint,
    UUID, String, DateTime, Boolean, and_, func
)
from sqlalchemy.orm import relationship

from app.exceptions.authorization_exceptions import EmailNotFoundException, BannedUserException
from app.models.ban_user import BanUser
from app.models.base import Base
from app.routes.auth import AccountIsNotVerifiedException
from app.utils.db import session_scope
from app.utils.engine import get_session


class UserRole(PyEnum):  # pylint: disable=C0115
    user = "user"
    parking_manager = "parking_manager"
    admin = "admin"


class User(Base):
    """Represents a user in the database."""

    __tablename__ = "user"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(UUID(as_uuid=True), default=uuid4, unique=True, nullable=False)
    nickname = Column(String(24), nullable=True)
    first_name = Column(String(50), nullable=True)
    middle_name = Column(String(50), nullable=True)
    last_name = Column(String(100), nullable=True)
    suffix = Column(String(5), nullable=True)
    email = Column(String(75), nullable=False, unique=True)
    phone_number = Column(String(15), nullable=False, unique=True)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.user)
    plate_number = Column(String(10), nullable=True, unique=True)
    otp_secret = Column(String(6), nullable=True)
    otp_expiry = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.current_timestamp()) # pylint: disable=E1102
    verification_token = Column(String(175), nullable=True)
    verification_expiry = Column(DateTime, nullable=True)
    is_verified = Column(Boolean, default=False, nullable=False)

    __table_args__ = (
        UniqueConstraint("email", name="user_email_key"),
        UniqueConstraint("phone_number", name="user_phone_number_key"),
        UniqueConstraint("plate_number", name="user_plate_number_key"),
        UniqueConstraint("uuid", name="user_uuid_key"),
        CheckConstraint(
            "role IN ('user', 'parking_manager', 'admin')", name="valid_role"
        ),
    )
    ban_user = relationship(
        "BanUser",
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="[BanUser.user_id]"
    )
    performed_audits = relationship(
        "AuditLog",
        back_populates="user_performed_by",
        cascade="all, delete-orphan",
        foreign_keys="[AuditLog.performed_by]"
    )
    targeted_audits = relationship(
        "AuditLog",
        back_populates="user_target",
        cascade="all, delete-orphan",
        foreign_keys="[AuditLog.target_user]"
    )
    establishment_documents = relationship(
        "EstablishmentDocument",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    company_profile = relationship(
        "CompanyProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    transactions = relationship(
        "ParkingTransaction",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def to_dict(self):
        """Converts the user object to a dictionary."""
        if self is None:
            return {}
        return {
            "user_id": self.user_id,
            "uuid": str(self.uuid),
            "nickname": self.nickname,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone_number": self.phone_number,
            "role": self.role.value if self.role else None,
            "plate_number": self.plate_number,
            "otp_secret": self.otp_secret,
            "otp_expiry": self.otp_expiry.isoformat() if self.otp_expiry else None,
            "is_verified": self.is_verified,
            "verification_token": self.verification_token,
            "verification_expiry": self.verification_expiry.isoformat()
            if self.verification_expiry else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    @staticmethod
    def get_user_id(user_uuid: bytes):
        """Get the user ID from the user UUID."""
        with session_scope() as session:
            user = session.execute(select(User).where(User.uuid == user_uuid)).scalar()
            return user.user_id


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
            new_user = User(**user_data)
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
                update(User).where(User.verification_token == token)
                .values(verification_token=None, verification_expiry=None, is_verified=True)
            )

    @staticmethod
    @overload
    def get_user(user_id: int = None) -> dict:
        """Get a user by their ID."""

    @staticmethod
    @overload
    def get_user(user_uuid: bytes = None) -> dict:
        """Get a user by their UUID."""

    @staticmethod
    @overload
    def get_user(email: str = None) -> dict:
        """Get a user by their email address."""

    @staticmethod
    @overload
    def get_user(plate_number: str = None) -> dict:
        """Get a user by their plate number."""

    @staticmethod
    def get_user(
        user_id: int = None, user_uuid: bytes = None, email: str = None, plate_number: str = None
    ):
        """
        Get a user by their ID, UUID, email address, or plate number.

        Parameters:
        user_id (int): The ID of the user.
        user_uuid (bytes): The UUID of the user.
        email (str): The email address of the user.
        plate_number (str): The plate number of the user.

        Returns:
        dict: A dictionary containing the user information.

        Raises:
        DataError, IntegrityError, OperationalError, DatabaseError: If there is an error
        during the database operation.
        """
        with session_scope() as session:
            user: User
            if user_id:
                user = session.execute(select(User).where(User.user_id == user_id)).scalar()
            elif user_uuid:
                user = session.execute(select(User).where(User.uuid == user_uuid)).scalar()
            elif email:
                user = session.execute(select(User).where(User.email == email)).scalar()
            elif plate_number:
                user = session.execute(
                    select(User).where(User.plate_number == plate_number)
                ).scalar()
            return user.to_dict()

class AuthOperations:  # pylint: disable=R0903 disable=C0115
    @classmethod
    def login_user(cls, email: str, role: str):
        """
        Authenticates a user by their email address.

        Parameters:
        email (str): The email address of the user attempting to log in.
        role (str): The role of the user attempting to log in.

        Returns:
        dict: A dictionary containing the user information

        Raises:
        EmailNotFoundException: If the email is not found in the database.
        OperationalError, DatabaseError: If there is an error during the database operation.
        """
        with session_scope() as session:
            user: User = session.execute(
                statement=select(User).where(and_(User.email == email, User.role == role))
            ).scalar()
            is_banned_user = session.execute(
                select(BanUser).where(BanUser.user_id == user.user_id)
            ).scalar()
            if user is None:
                raise EmailNotFoundException("Email not found.")
            if user.is_verified is False:
                raise AccountIsNotVerifiedException("Account is not verified.")
            if is_banned_user is not None:
                raise BannedUserException("User is banned.")
            return user.to_dict()


class OTPOperations:
    """Class to handle operations related to OTP."""

    @classmethod
    def get_otp(cls, email: str) -> dict:
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
        with session_scope() as session:
            user: User = session.execute(select(User).where(User.email == email)).scalar()
            if user is None:
                raise EmailNotFoundException("Email not found.")
            return user.to_dict()

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
        with session_scope() as session:
            session.execute(
                update(User).where(User.email == data.get("email"))
                .values(otp_secret=data.get("otp_secret"), otp_expiry=data.get("otp_expiry"))
            )
            session.commit()

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
        with get_session() as session:
            session.execute(
                update(User).where(User.email == email).values(otp_secret=None, otp_expiry=None)
            )
            session.commit()
