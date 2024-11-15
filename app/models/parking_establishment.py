"""
    SQLAlchemy model representing a parking establishment.
    Contains details about a parking facility including location, operating hours,
    pricing and relationships with slots and manager. Provides methods to convert
    the model instance to a dictionary format.
"""

# pylint: disable=E1102

from sqlalchemy import (
    VARCHAR,
    Boolean,
    Column,
    Integer,
    BINARY,
    TIME,
    DECIMAL,
    and_,
    func,
    update,
    ForeignKey,
    TIMESTAMP,
    case,
)
from sqlalchemy.exc import OperationalError, DatabaseError, IntegrityError, DataError
from sqlalchemy.orm import relationship

from app.exceptions.establishment_lookup_exceptions import (
    EstablishmentDoesNotExist,
    EstablishmentEditsNotAllowedException,
)
from app.models.base import Base
from app.models.slot import Slot
from app.utils.engine import get_session


class ParkingEstablishment(Base):  # pylint: disable=R0903 disable=C0115
    __tablename__ = "parking_establishment"

    establishment_id = Column(Integer, primary_key=True)
    manager_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    uuid = Column(BINARY(16), nullable=False)
    name = Column(VARCHAR(255), nullable=False)
    address = Column(VARCHAR(255), nullable=False)
    contact_number = Column(VARCHAR(25), nullable=False)
    opening_time = Column(TIME, nullable=False)
    closing_time = Column(TIME, nullable=False)
    is_24_hours = Column(Boolean, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)
    updated_at = Column(TIMESTAMP, nullable=False)
    hourly_rate = Column(DECIMAL(8, 2), nullable=False)
    longitude = Column(DECIMAL(9, 6), nullable=False)
    latitude = Column(DECIMAL(9, 6), nullable=False)

    slot = relationship(
        "Slot", back_populates="parking_establishment", cascade="all, delete-orphan"
    )
    user = relationship("User", back_populates="parking_establishment")

    def to_dict(self):
        """Convert the ParkingEstablishment instance to a dictionary."""
        return {
            "establishment_id": self.establishment_id,
            "uuid": self.uuid.hex(),
            "name": self.name,
            "address": self.address,
            "contact_number": self.contact_number,
            "opening_time": str(self.opening_time),
            "closing_time": str(self.closing_time),
            "is_24_hours": self.is_24_hours,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "hourly_rate": float(self.hourly_rate),  # type: ignore
            "longitude": float(self.longitude),  # type: ignore
            "latitude": float(self.latitude),  # type: ignore
        }

    def calculate_distance_from(self, latitude: float, longitude: float) -> float:
        """Calculate distance from given coordinates to this establishment"""
        radius_km = 6371
        return radius_km * func.acos(
            func.cos(func.radians(latitude))
            * func.cos(func.radians(self.latitude))
            * func.cos(func.radians(self.longitude) - func.radians(longitude))
            + func.sin(func.radians(latitude)) * func.sin(func.radians(self.latitude))
        )  # type: ignore

    @classmethod
    def order_by_distance(
        cls, latitude: float, longitude: float, ascending: bool = True
    ):
        """Get order_by expression for distance-based sorting"""
        radius_km = 6371
        distance_formula = radius_km * func.acos(
            func.cos(func.radians(latitude))
            * func.cos(func.radians(cls.latitude))
            * func.cos(func.radians(cls.longitude) - func.radians(longitude))
            + func.sin(func.radians(latitude)) * func.sin(func.radians(cls.latitude))
        )
        return distance_formula.asc() if ascending else distance_formula.desc()


class GetEstablishmentOperations:
    """Class for operations related to parking establishment (Getting)."""

    @staticmethod
    def is_establishment_exists(establishment_id: int):
        """
        Checks if a parking establishment exists in the database by its ID.

        Args:
            establishment_id (int): The ID of the parking establishment to check.

        Returns:
            bool: True if the establishment exists, False otherwise.

        Raises:
            OperationalError: If there is a database operation error.
        """
        session = get_session()
        try:
            return (
                session.query(ParkingEstablishment)
                .filter(ParkingEstablishment.establishment_id == establishment_id)
                .count()
                > 0
            )
        except OperationalError as err:
            raise err
        finally:
            session.close()

    @staticmethod
    def get_establishment_by_id(establishment_id: int):
        """
        Retrieves a parking establishment from the database by its ID.

        Args:
            establishment_id (int): The ID of the parking establishment to retrieve.

        Returns:
            ParkingEstablishment: The parking establishment object if found, None otherwise.

        Raises:
            OperationalError: If there is a database operation error.
        """
        session = get_session()
        try:
            establishment = (
                session.query(ParkingEstablishment)
                .filter(ParkingEstablishment.establishment_id == establishment_id)
                .first()
            )
            return establishment
        except OperationalError as err:
            raise err
        finally:
            session.close()
    # pylint: disable=R0914
    @staticmethod
    def get_establishments(query_dict: dict):
        """
        Combined query for establishments with optional filters
        """
        session = get_session()
        try:
            # Base query with slot statistics
            establishment_name = query_dict.get("establishment_name")
            latitude = query_dict.get("latitude")
            longitude = query_dict.get("longitude")
            is_24_hours = query_dict.get("is_24_hours")
            vehicle_type_id = query_dict.get("vehicle_type_id")
            query = (
                session.query(
                    ParkingEstablishment,
                    func.count(case((Slot.slot_status == "open", 1))).label("open_slots"),
                    func.count(case((Slot.slot_status == "occupied", 1))).label("occupied_slots"),
                    func.count(case((Slot.slot_status == "reserved", 1))).label("reserved_slots"),
                )
                .outerjoin(Slot)
                .group_by(ParkingEstablishment.establishment_id)
            )

            if is_24_hours is not None:
                query = query.filter(ParkingEstablishment.is_24_hours == is_24_hours)

            if vehicle_type_id is not None:
                query = query.filter(Slot.vehicle_type_id == vehicle_type_id)
            if establishment_name is not None:
                query = query.filter(ParkingEstablishment.name.ilike(f"%{establishment_name}%"))

            if latitude is not None and longitude is not None:
                query = query.order_by(
                    ParkingEstablishment.order_by_distance(
                        latitude=latitude,
                        longitude=longitude,
                        ascending=True
                    )
                )

            establishments = query.all()

            # Format results
            result = []
            for establishment, open_count, occupied_count, reserved_count in establishments:
                establishment_dict = establishment.to_dict()
                establishment_dict.update({
                    "slot_statistics": {
                        "open_slots": open_count,
                        "occupied_slots": occupied_count,
                        "reserved_slots": reserved_count,
                        "total_slots": open_count + occupied_count + reserved_count,
                    }
                })
                result.append(establishment_dict)

            return result

        except OperationalError as err:
            raise err
        finally:
            session.close()


class CreateEstablishmentOperations:  # pylint: disable=R0903
    """
    Class that handles the creation of new parking establishments in the database.
    Provides a static method to create establishments using provided data dictionary.
    Handles database session management and error handling for establishment creation.
    """

    @staticmethod
    def create_establishment(establishment_data: dict):
        """
        Creates a new parking establishment in the database using provided data.

        Args:
            establishment_data (dict): Dictionary containing establishment details including uuid,
                manager_id, name, address, contact info, hours, rates and coordinates.

        Raises:
            OperationalError: If there is a problem with database operations
            DatabaseError: If there is a general database error
            DataError: If there is an issue with the data format
            IntegrityError: If there is a violation of database constraints
        """
        session = get_session()
        try:
            establishment = ParkingEstablishment(
                uuid=establishment_data.get("uuid"),
                manager_id=establishment_data.get("manager_id"),
                name=establishment_data.get("name"),
                address=establishment_data.get("address"),
                contact_number=establishment_data.get("contact_number"),
                opening_time=establishment_data.get("opening_time"),
                closing_time=establishment_data.get("closing_time"),
                is_24_hours=establishment_data.get("is_24_hours"),
                created_at=establishment_data.get("created_at"),
                updated_at=establishment_data.get("updated_at"),
                hourly_rate=establishment_data.get("hourly_rate"),
                longitude=establishment_data.get("longitude"),
                latitude=establishment_data.get("latitude"),
            )
            session.add(establishment)
            session.commit()
        except (OperationalError, DatabaseError, DataError, IntegrityError) as err:
            session.rollback()
            raise err
        finally:
            session.close()


class UpdateEstablishmentOperations:  # pylint: disable=R0903
    """
    Class that handles update operations for parking establishments.

    This class provides functionality to update parking establishment details in the database.
    Validates establishment existence and manager permissions before allowing updates.
    Handles database operations with proper session management and error handling.
    """

    @staticmethod
    def update_establishment(establishment_id: int, establishment_data: dict):
        """
        Updates a parking establishment's details in the database.

        Args:
            establishment_id (int): The ID of the parking establishment to update.
            establishment_data (dict): Dictionary containing the updated establishment details.

        Raises:
            EstablishmentDoesNotExist: If the establishment with given ID does not exist.
            EstablishmentEditsNotAllowedException: If the manager_id does not match the
            establishment.
            OperationalError: If there is a database operation error.
            DatabaseError: If there is a database-related error.
            DataError: If there is an error with the data format.
            IntegrityError: If there is a database integrity constraint violation.
        """
        session = get_session()
        try:
            is_establishment_exists = (
                GetEstablishmentOperations.is_establishment_exists(establishment_id)
            )
            if not is_establishment_exists:
                raise EstablishmentDoesNotExist("Establishment does not exist")
            is_allowed_to_make_edits = (
                session.query(ParkingEstablishment).filter(
                    and_(
                        ParkingEstablishment.establishment_id == establishment_id,
                        ParkingEstablishment.manager_id
                        == establishment_data.get("manager_id"),
                    )
                )
            ).count()
            if not is_allowed_to_make_edits:
                raise EstablishmentEditsNotAllowedException(
                    "You are not allowed to make edits to this establishment."
                )
            session.execute(
                update(ParkingEstablishment)
                .where(
                    and_(
                        ParkingEstablishment.establishment_id == establishment_id,
                        ParkingEstablishment.manager_id
                        == establishment_data.get("manager_id"),
                    )
                )
                .values(
                    {
                        "name": establishment_data.get("name"),
                        "address": establishment_data.get("address"),
                        "contact_number": establishment_data.get("contact_number"),
                        "opening_time": establishment_data.get("opening_time"),
                        "closing_time": establishment_data.get("closing_time"),
                        "is_24_hours": establishment_data.get("is_24_hours"),
                        "hourly_rate": establishment_data.get("hourly_rate"),
                        "longitude": establishment_data.get("longitude"),
                        "latitude": establishment_data.get("latitude"),
                        "updated_at": establishment_data.get("updated_at"),
                    }
                )
            )
            session.commit()
        except (OperationalError, DatabaseError, DataError, IntegrityError) as err:
            session.rollback()
            raise err
        finally:
            session.close()


class DeleteEstablishmentOperations:  # pylint: disable=R0903
    """
    Class for managing deletion operations of parking establishments.
    Provides functionality to safely remove parking establishment records from the database
    while handling database transaction errors and ensuring proper session management.
    """

    @staticmethod
    def delete_establishment(establishment_id: int):
        """
        Deletes a parking establishment from the database by its ID.

        Args:
            establishment_id (int): The unique identifier of the parking establishment to delete.

        Raises:
            OperationalError: If there is a problem with database operations.
            DatabaseError: If there is a general database error.
            DataError: If there is an issue with the data format.
            IntegrityError: If deletion violates database integrity constraints.
        """
        session = get_session()
        try:
            establishment = (
                session.query(ParkingEstablishment)
                .filter(ParkingEstablishment.establishment_id == establishment_id)
                .first()
            )
            session.delete(establishment)
            session.commit()
        except (OperationalError, DatabaseError, DataError, IntegrityError) as err:
            session.rollback()
            raise err
        finally:
            session.close()
