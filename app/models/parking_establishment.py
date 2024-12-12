"""
    SQLAlchemy model representing a parking establishment.
    Contains details about a parking facility including location, operating hours,
    pricing and relationships with slots and manager. Provides methods to convert
    the model instance to a dictionary format.
"""

# pylint: disable=E1102, C0415

from typing import Union, overload
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    Text,
    UUID,
    DECIMAL,
    func,
    update,
    ForeignKey,
    TIMESTAMP,
    case,
    CheckConstraint,
    String,
)
from sqlalchemy.exc import OperationalError, DatabaseError
from sqlalchemy.orm import relationship

from app.exceptions.establishment_lookup_exceptions import (
    EstablishmentDoesNotExist,
)
from app.models.base import Base
from app.utils.db import session_scope
from app.utils.engine import get_session


class ParkingEstablishment(Base):  # pylint: disable=too-few-public-methods, missing-class-docstring
    __tablename__ = "parking_establishment"

    establishment_id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(UUID, default=uuid4, unique=True)
    profile_id = Column(
        Integer, ForeignKey("company_profile.profile_id"), nullable=False
    )
    space_type = Column(String(20), nullable=False)
    space_layout = Column(String(20), nullable=False)
    custom_layout = Column(Text)
    dimensions = Column(Text)
    is24_7 = Column(Boolean, default=False)
    access_info = Column(Text)
    custom_access = Column(Text)
    status = Column(String(20), default="pending")
    created_at = Column(TIMESTAMP, default=func.current_timestamp())
    updated_at = Column(
        TIMESTAMP, default=func.current_timestamp(), onupdate=func.current_timestamp()
    )
    name = Column(String(255), nullable=False)
    lighting = Column(Text, nullable=False)
    accessibility = Column(Text, nullable=False)
    nearby_landmarks = Column(Text, nullable=True)
    longitude = Column(DECIMAL(precision=9, scale=6), nullable=False)
    latitude = Column(DECIMAL(precision=9, scale=6), nullable=False)
    facilities = Column(Text, nullable=False)

    # Constraints (Space Layout, Space Type, and Status check constraints)
    __table_args__ = (
        CheckConstraint(
            "space_layout IN ('parallel', 'perpendicular', 'angled', 'other')",
            name="parking_establishment_space_layout_check",
        ),
        CheckConstraint(
            "space_type IN ('indoor', 'outdoor', 'covered', 'uncovered')",
            name="parking_establishment_space_type_check",
        ),
        CheckConstraint(
            "status IN ('pending', 'approved', 'rejected')",
            name="parking_establishment_status_check",
        ),
    )

    company_profile = relationship("CompanyProfile", back_populates="parking_establishments")
    documents = relationship("EstablishmentDocument", back_populates="parking_establishment")
    operating_hours = relationship("OperatingHour", back_populates="parking_establishment")
    parking_slots = relationship("ParkingSlot", back_populates="parking_establishment")
    payment_methods = relationship("PaymentMethod", back_populates="parking_establishment")

    def to_dict(self):
        """Convert the ParkingEstablishment instance to a dictionary."""
        if self is None:
            return {}
        return {
            "establishment_id": self.establishment_id,
            "uuid": str(self.uuid),
            "profile_id": self.profile_id,
            "space_type": self.space_type,
            "space_layout": self.space_layout,
            "custom_layout": self.custom_layout,
            "dimensions": self.dimensions,
            "is24_7": self.is24_7,
            "access_info": self.access_info,
            "custom_access": self.custom_access,
            "status": self.status,
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at),
            "name": self.name,
            "lighting": self.lighting,
            "accessibility": self.accessibility,
            "nearby_landmarks": self.nearby_landmarks,
            "longitude": float(self.longitude),
            "latitude": float(self.latitude),
            "facilities": self.facilities,
        }

    def calculate_distance_from(self, latitude: float, longitude: float) -> float:
        """Calculate distance from given coordinates to this establishment"""
        radius_km = 6371
        return radius_km * func.acos(
            func.cos(func.radians(latitude))
            * func.cos(func.radians(self.latitude))
            * func.cos(func.radians(self.longitude) - func.radians(longitude))
            + func.sin(func.radians(latitude)) * func.sin(func.radians(self.latitude))
        )

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

    @staticmethod
    def get_establishment_id(establishment_uuid: bytes):
        """Get establishment ID by UUID"""
        with session_scope() as session:
            establishment = (
                session.query(ParkingEstablishment)
                .filter(ParkingEstablishment.uuid == establishment_uuid)
                .first()
            )
            return establishment.establishment_id


class GetEstablishmentOperations:
    """Class for operations related to parking establishment (Getting)."""

    @staticmethod
    def get_establishment_id_by_uuid(establishment_uuid: bytes):
        """
        Retrieves the ID of a parking establishment from the database by its UUID.

        Args:
            establishment_uuid (bytes): The UUID of the parking establishment to retrieve.

        Returns:
            int: The ID of the parking establishment if found, None otherwise.

        Raises:
            OperationalError: If there is a database operation error.
        """
        session = get_session()
        try:
            establishment = (
                session.query(ParkingEstablishment)
                .filter(ParkingEstablishment.uuid == establishment_uuid)
                .first()
            )
            if establishment is None:
                raise EstablishmentDoesNotExist("Establishment does not exist")
            return establishment.establishment_id
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
        # pylint: disable=cyclic-import
        from app.models.parking_slot import ParkingSlot

        session = get_session()
        try:
            establishment_name = query_dict.get("establishment_name")
            latitude = query_dict.get("latitude")
            longitude = query_dict.get("longitude")
            is_24_hours = query_dict.get("is_24_hours")
            vehicle_type_id = query_dict.get("vehicle_type_id")
            query = (
                session.query(
                    ParkingEstablishment,
                    func.count(case((ParkingSlot.slot_status == "open", 1))).label(
                        "open_slots"
                    ),
                    func.count(case((ParkingSlot.slot_status == "occupied", 1))).label(
                        "occupied_slots"
                    ),
                    func.count(case((ParkingSlot.slot_status == "reserved", 1))).label(
                        "reserved_slots"
                    ),
                )
                .outerjoin(ParkingSlot)
                .group_by(ParkingEstablishment.establishment_id)
            )

            if is_24_hours is not None:
                query = query.filter(ParkingEstablishment.is_24_hours == is_24_hours)

            if vehicle_type_id is not None:
                query = query.filter(ParkingSlot.vehicle_type_id == vehicle_type_id)
            if establishment_name is not None:
                query = query.filter(
                    ParkingEstablishment.name.ilike(f"%{establishment_name}%")
                )

            if latitude is not None and longitude is not None:
                query = query.order_by(
                    ParkingEstablishment.order_by_distance(
                        latitude=latitude, longitude=longitude, ascending=True
                    )
                )

            establishments = query.all()

            result = []
            for (
                establishment,
                open_count,
                occupied_count,
                reserved_count,
            ) in establishments:
                establishment_dict = establishment.to_dict()
                establishment_dict.update(
                    {
                        "slot_statistics": {
                            "open_slots": open_count,
                            "occupied_slots": occupied_count,
                            "reserved_slots": reserved_count,
                            "total_slots": open_count + occupied_count + reserved_count,
                        }
                    }
                )
                result.append(establishment_dict)

            return result

        except (OperationalError, DatabaseError) as error:
            raise error
        finally:
            session.close()


class ParkingEstablishmentRepository:  # pylint: disable=R0903
    """Class for operations related to parking establishment"""
    @staticmethod
    def create_establishment(establishment_data: dict):
        """Create a new parking establishment."""
        with session_scope() as session:
            new_parking_establishment = ParkingEstablishment(**establishment_data)
            session.add(new_parking_establishment)
            session.flush()
            return new_parking_establishment.establishment_id

    @staticmethod
    @overload
    def get_establishment(establishment_uuid: bytes) -> dict:
        """Get parking establishment by UUID."""

    @staticmethod
    @overload
    def get_establishment(profile_id: int) -> dict:
        """Get parking establishment by profile id."""

    @staticmethod
    @overload
    def get_establishment(establishment_id: int) -> dict:
        """Get parking establishment by establishment id."""

    @staticmethod
    def get_establishment(
        establishment_uuid: bytes = None, profile_id: int = None, establishment_id: int = None
    ) -> Union[dict]:
        """Get parking establishment by UUID, profile id, or establishment id."""
        with session_scope() as session:
            if establishment_id is not None:
                establishment = (
                    session.query(ParkingEstablishment)
                    .filter(ParkingEstablishment.establishment_id == establishment_id)
                    .first()
                )
                return establishment.to_dict() if establishment else {}
            if profile_id is not None:
                establishment = (
                    session.query(ParkingEstablishment)
                    .filter(ParkingEstablishment.profile_id == profile_id)
                    .first()
                )
                return establishment.to_dict()
            if establishment_uuid is not None:
                establishment = (
                    session.query(ParkingEstablishment)
                    .filter(ParkingEstablishment.uuid == establishment_uuid)
                    .first()
                )
                return establishment.to_dict() if establishment else {}
            return {}

    @staticmethod
    def update_parking_establishment(establishment_data: dict):
        """Update parking establishment details."""
        with session_scope() as session:
            establishment_id = ParkingEstablishment.get_establishment_id(
                establishment_uuid=establishment_data.get("establishment_uuid")
            )
            session.execute(
                update(ParkingEstablishment)
                .where(ParkingEstablishment.establishment_id == establishment_id)
                .values(establishment_data)
            )
            session.commit()
