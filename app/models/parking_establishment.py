"""
    SQLAlchemy model representing a parking establishment.
    Contains details about a parking facility including location, operating hours,
    pricing and relationships with slots and manager. Provides methods to convert
    the model instance to a dictionary format.
"""

# pylint: disable=E1102, C0415, disable=too-few-public-methods

from typing import Union, overload
from uuid import uuid4

from sqlalchemy import (
    Boolean, Column, Integer, Text, UUID, DECIMAL, func, update, ForeignKey, TIMESTAMP,
    CheckConstraint, String,
)
from sqlalchemy.orm import relationship

from app.exceptions.establishment_lookup_exceptions import EstablishmentDoesNotExist
from app.models.base import Base
from app.models.parking_slot import ParkingSlot
from app.utils.db import session_scope


class ParkingEstablishment(Base):
    """Define the parking_establishment table model."""
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
    verified = Column(Boolean, default=False)

    __table_args__ = (
        CheckConstraint(
            "space_layout IN ('parallel', 'perpendicular', 'angled', 'other')",
            name="parking_establishment_space_layout_check",
        ),
        CheckConstraint(
            "space_type IN ('indoor', 'outdoor', 'covered', 'uncovered')",
            name="parking_establishment_space_type_check",
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
            "verified": self.verified,
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at),
            "name": self.name,
            "lighting": self.lighting,
            "accessibility": self.accessibility,
            "nearby_landmarks": self.nearby_landmarks.title() if self.nearby_landmarks else '',
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
    def get_establishment_id(establishment_uuid: str):
        """Get establishment ID by UUID"""
        with session_scope() as session:
            establishment = (
                session.query(ParkingEstablishment)
                .filter(ParkingEstablishment.uuid == establishment_uuid)
                .first()
            )
            return establishment.establishment_id


class ParkingEstablishmentRepository:
    """Class for operations related to parking establishment"""
    @staticmethod
    def create_establishment(establishment_data: dict):
        """Create a new parking establishment."""
        with session_scope() as session:
            new_parking_establishment = ParkingEstablishment(**establishment_data)
            session.add(new_parking_establishment)
            session.commit()
            return new_parking_establishment.establishment_id
    @staticmethod
    @overload
    def get_establishments(verification_status: bool) -> list:
        """Get parking establishments by verification status."""
    @staticmethod
    @overload
    def get_establishments(
        establishment_name: str = None, user_longitude: float = None, user_latitude: float = None
    ) -> list:
        """Get all parking establishments."""
    @staticmethod
    @overload
    def get_establishments() -> list:
        """Get all parking establishments."""
    @staticmethod
    def get_establishments(
        verification_status: bool = None, establishment_name: str = None,
        user_longitude: float = None, user_latitude: float = None
    ) -> list:
        """Get parking establishments by verification status."""
        with session_scope() as session:
            if verification_status is not None:
                establishments = (
                    session.query(ParkingEstablishment)
                    .filter(ParkingEstablishment.verified == verification_status)
                    .all()
                )
                return [establishment.to_dict() for establishment in establishments]
            if user_longitude is not None and user_latitude is not None:
                query = session.query(
                    ParkingEstablishment,
                    func.count(ParkingSlot.slot_id).label("total_slots"),
                    func.count(ParkingSlot.slot_id).filter(
                        ParkingSlot.slot_status == "open").label("open_slots"),
                    func.count(ParkingSlot.slot_id).filter(
                        ParkingSlot.slot_status == "occupied").label("occupied_slots"),
                    func.count(ParkingSlot.slot_id).filter(
                        ParkingSlot.slot_status == "reserved").label("reserved_slots")
                ).outerjoin(ParkingSlot).group_by(ParkingEstablishment.establishment_id).where(
                    ParkingEstablishment.verified.is_(True)
                )
                if establishment_name is not None:
                    query = query.filter(ParkingEstablishment.name.ilike(f"%{establishment_name}%"))
                if user_longitude is not None and user_latitude is not None:
                    query = query.order_by(
                        ParkingEstablishment.order_by_distance(
                            latitude=user_latitude, longitude=user_longitude, ascending=True
                        )
                    )
                establishments = query.all()
                result = []
                for establishment, total_slots, open_slots, occupied_slots, reserved_slots in \
                    establishments:
                    establishment_dict = establishment.to_dict()
                    establishment_dict.update({
                        "total_slots": total_slots,
                        "open_slots": open_slots,
                        "occupied_slots": occupied_slots,
                        "reserved_slots": reserved_slots,
                    })
                    result.append(establishment_dict)
                return result
            establishments = session.query(ParkingEstablishment).all()
            return [establishment.to_dict() for establishment in establishments]
    @staticmethod
    @overload
    def get_establishment(establishment_uuid: str) -> dict:
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
        establishment_uuid: str = None, profile_id: int = None, establishment_id: int = None
    ) -> Union[dict]:
        """Get parking establishment by UUID, profile id, or establishment id."""
        with session_scope() as session:
            establishment: ParkingEstablishment
            if establishment_id is not None:
                establishment = (
                    session.query(ParkingEstablishment)
                    .filter(ParkingEstablishment.establishment_id == establishment_id)
                    .first()
                )
            elif profile_id is not None:
                establishment = (
                    session.query(ParkingEstablishment)
                    .filter(ParkingEstablishment.profile_id == profile_id)
                    .first()
                )
            elif establishment_uuid is not None:
                establishment = (
                    session.query(ParkingEstablishment)
                    .filter(ParkingEstablishment.uuid == establishment_uuid)
                    .first()
                )
            if establishment is None:
                raise EstablishmentDoesNotExist("Establishment does not exist.")
            return establishment.to_dict()
    @staticmethod
    def update_parking_establishment(establishment_data: dict, establishment_id: int):
        """Update parking establishment details."""
        with session_scope() as session:
            immutable_fields = [
                'establishment_uuid', 'uuid',
                'establishment_id', 'profile_id', 'created_at'
            ]
            update_data = {k: v for k, v in establishment_data.items() if k not in immutable_fields}

            session.execute(
                update(ParkingEstablishment)
                .where(ParkingEstablishment.establishment_id == establishment_id)
                .values(update_data)
            )
            session.commit()
    @staticmethod
    def verify_parking_establishment(establishment_uuid: bytes):
        """Verify a parking establishment."""
        with session_scope() as session:
            establishment_id = ParkingEstablishment.get_establishment_id(establishment_uuid)
            session.execute(
                update(ParkingEstablishment)
                .where(ParkingEstablishment.establishment_id == establishment_id)
                .values(verified=True)
            )
            session.commit()
