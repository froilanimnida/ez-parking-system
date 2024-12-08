"""
    Represents a vehicle type entity in the database.

    Attributes:
        vehicle_id (int): Primary key for the vehicle type.
        code (str): Unique code for the vehicle type.
        name (str): Name of the vehicle type.
        description (str): Description of the vehicle type.
        size_category (Enum): Size category of the vehicle type, can be SMALL, MEDIUM, or LARGE.
        base_rate_multiplier (Decimal): Multiplier for the base rate.
        is_active (bool): Indicates if the vehicle type is active.
        created_at (DateTime): Timestamp when the vehicle type was created.
        updated_at (DateTime): Timestamp when the vehicle type was last updated.

    Relationships:
        slot: Establishes a relationship with the Slot model, allowing cascading delete-orphan
        operations.
"""

# pylint: disable=R0801

from enum import Enum as PyEnum

from sqlalchemy import (
    BOOLEAN,
    Column,
    Integer,
    Enum,
    func,
    DateTime,
    update, String, TIMESTAMP,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.exc import IntegrityError, OperationalError, DatabaseError, DataError
from sqlalchemy.orm import relationship

from app.exceptions.vehicle_type_exceptions import VehicleTypeDoesNotExist
from app.models.base import Base
from app.utils.engine import get_session


class SizeCategory(PyEnum):
    SMALL = 'Small'
    MEDIUM = 'Medium'
    LARGE = 'Large'

class VehicleType(Base):
    __tablename__ = 'vehicle_type'
    
    # Columns definition
    vehicle_type_id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False, default=func.uuid_generate_v4())
    code = Column(String(45), nullable=False)
    name = Column(String(125), nullable=False)
    description = Column(String(255), nullable=False)
    size_category = Column(Enum(SizeCategory), nullable=False)
    is_active = Column(BOOLEAN, default=True, nullable=False)
    created_at = Column(TIMESTAMP, default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    def __repr__(self):
        return f"<VehicleType(vehicle_type_id={self.vehicle_type_id}, code={self.code}, name={self.name}, size_category={self.size_category})>"


    slot = relationship(
        "Slot", back_populates="vehicle_type", cascade="all, delete-orphan"
    )
    parking_transaction = relationship(
        "ParkingTransaction",
        back_populates="vehicle_type",
        cascade="all, delete-orphan",
    )

    def to_dict(self):
        """Returns the data representation of the vehicle type object."""
        return {
            "vehicle_type_id": self.vehicle_type_id,
            "code": self.code,
            "name": self.name,
            "description": self.description,
            "size_category": self.size_category,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class VehicleTypeOperations:  # pylint: disable=R0903 disable=C0115

    @classmethod
    def is_vehicle_type_exist(cls, vehicle_type_id: int):
        """
        Check if a vehicle type exists in the database based on its code.

        Parameters:
        vehicle_type_id (int): The ID of the vehicle type to check.

        Returns:
        bool: True if the vehicle type exists, False otherwise.

        Raises:
        IntegrityError, OperationalError, DatabaseError, DataError: If any database error occurs
        during the operation.
        """
        session = get_session()
        try:
            vehicle_type = (
                session.query(VehicleType)
                .filter(VehicleType.vehicle_type_id == vehicle_type_id)
                .first()
            )
            if vehicle_type is None:
                raise VehicleTypeDoesNotExist("Vehicle type does not exist.")
        except (IntegrityError, OperationalError, DatabaseError, DataError) as e:
            raise e
        finally:
            session.close()

    @classmethod
    def get_vehicle_type_by_id(cls, vehicle_type_id: int):
        """
        Retrieve a vehicle type from the database by its ID.

        Parameters:
        vehicle_type_id (int): The unique identifier of the vehicle type to retrieve.

        Returns:
        VehicleType: The vehicle type object if found, otherwise None.

        Raises:
        OperationalError: If an error occurs during the database operation.
        """
        session = get_session()
        try:
            vehicle_type = (
                session.query(VehicleType)
                .filter(VehicleType.vehicle_type_id == vehicle_type_id)
                .first()
            )
            return {} if vehicle_type is None else vehicle_type.to_dict()
        except OperationalError as error:
            raise error
        finally:
            session.close()

    @classmethod
    def create_new_vehicle_type(cls, vehicle_type_data: dict):  # pylint: disable=C0116
        """
        Creates a new vehicle type in the database.

        Parameters:
        vehicle_type_data (dict): A dictionary containing the necessary data to create a
        new vehicle type.
            The dictionary should have the following keys:
            - code (str): The unique code for the vehicle type.
            - name (str): The name of the vehicle type.
            - description (str): A brief description of the vehicle type.
            - size_category (str): The size category of the vehicle type
                (e.g., SMALL, MEDIUM, LARGE).
            - base_rate_multiplier (float): The base rate multiplier for the vehicle type.
            - is_active (bool): A flag indicating whether the vehicle type is active or not.
            - created_at (datetime): The date and time when the vehicle type was created.
            - updated_at (datetime): The date and time when the vehicle type was last updated.

        Returns:
        None

        Raises:
        IntegrityError, OperationalError, DatabaseError, DataError: If any database error occurs
        during the operation.
        """
        session = get_session()
        try:
            new_vehicle_type = VehicleType(
                code=vehicle_type_data["code"],
                name=vehicle_type_data["name"],
                description=vehicle_type_data["description"],
                size_category=vehicle_type_data["size_category"],
                is_active=vehicle_type_data["is_active"],
                created_at=vehicle_type_data["created_at"],
                updated_at=vehicle_type_data["updated_at"],
            )
            session.add(new_vehicle_type)
            session.commit()
        except (IntegrityError, OperationalError, DatabaseError, DataError) as err:
            session.rollback()
            raise err
        finally:
            session.close()

    @classmethod
    def update_vehicle_type(cls, vehicle_id: int, vehicle_type_data: dict):
        """
        Updates an existing vehicle type in the database.

        Parameters:
        vehicle_id (int): The ID of the vehicle type to update.
        vehicle_type_data (dict): Dictionary containing updated vehicle type information.
            Must include: code, name, description, size_category, base_rate_multiplier,
            is_active, and updated_at.

        Raises:
        VehicleTypeDoesNotExist: If the specified vehicle type is not found.
        IntegrityError, OperationalError, DatabaseError, DataError: If any database error occurs.
        """
        session = get_session()
        try:
            is_vehicle_type_exist = cls.is_vehicle_type_exist(
                VehicleType(vehicle_type_id=vehicle_id)
            ) and cls.is_vehicle_type_exist(VehicleType(vehicle_id=vehicle_id))
            if not is_vehicle_type_exist:
                raise VehicleTypeDoesNotExist("Vehicle type does not exist.")
            session.execute(
                update(VehicleType)
                .where(VehicleType.vehicle_type_id == vehicle_id)
                .values(
                    code=vehicle_type_data["code"],
                    name=vehicle_type_data["name"],
                    description=vehicle_type_data["description"],
                    size_category=vehicle_type_data["size_category"],
                    base_rate_multiplier=vehicle_type_data["base_rate_multiplier"],
                    is_active=vehicle_type_data["is_active"],
                    updated_at=vehicle_type_data["updated_at"],
                )
            )
            session.commit()
        except (IntegrityError, OperationalError, DatabaseError, DataError) as err:
            session.rollback()
            raise err
        finally:
            session.close()

    @classmethod
    def get_vehicle_type(cls, vehicle_id: int):
        """
        Retrieve a vehicle type from the database by its ID.

        Parameters:
        vehicle_id (int): The unique identifier of the vehicle type to retrieve.

        Returns:
        VehicleType: The vehicle type object if found, otherwise None.

        Raises:
        OperationalError: If an error occurs during the database operation.
        """
        session = get_session()
        try:
            vehicle_type = (
                session.query(VehicleType)
                .filter(VehicleType.vehicle_type_id == vehicle_id)
                .first()
            )
            return vehicle_type
        except (OperationalError, DatabaseError) as error:
            raise error
        finally:
            session.close()


class VehicleRepository:  # pylint: disable=R0903
    """Class for vehicle repository operations."""

    @classmethod
    def get_all_vehicle_types(cls):
        """Get all vehicle types from the database."""
        session = get_session()
        try:
            vehicle_types = session.query(VehicleType).all()
            return [vehicle_type.to_dict() for vehicle_type in vehicle_types]
        except (OperationalError, DatabaseError) as error:
            raise error
        finally:
            session.close()
