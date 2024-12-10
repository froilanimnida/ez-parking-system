"""
    Represents a vehicle type entity in the database.
"""

# pylint: disable=R0801, E1102

from enum import Enum as PyEnum
from typing import overload

from sqlalchemy import BOOLEAN, Column, Integer, Enum, func, String, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.utils.db import session_scope


class SizeCategory(PyEnum):
    """Enum class for vehicle size categories."""
    SMALL = 'Small'
    MEDIUM = 'Medium'
    LARGE = 'Large'

class VehicleType(Base):
    """ Represents the vehicle type entity in the database. """
    __tablename__ = 'vehicle_type'

    vehicle_type_id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False, default=func.uuid_generate_v4())
    code = Column(String(45), nullable=False)
    name = Column(String(125), nullable=False)
    description = Column(String(255), nullable=False)
    size_category = Column(Enum(SizeCategory), nullable=False)
    is_active = Column(BOOLEAN, default=True, nullable=False)
    created_at = Column(TIMESTAMP, default=func.current_timestamp())
    updated_at = Column(
        TIMESTAMP, default=func.current_timestamp(), onupdate=func.current_timestamp()
    )

    parking_slots = relationship(
        "ParkingSlot", back_populates="vehicle_type", cascade="all, delete-orphan"
    )
    parking_transactions = relationship(
        "ParkingTransaction", back_populates="vehicle_type", cascade="all, delete-orphan"
    )

    def to_dict(self):
        """Returns the data representation of the vehicle type object."""
        if self is None:
            return {}
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

    @staticmethod
    def get_vehicle_type_id(vehicle_type_uuid: bytes):
        """Get vehicle type ID by UUID."""
        with session_scope() as session:
            vehicle_type = session.query(VehicleType).filter_by(uuid=vehicle_type_uuid).first()
            return vehicle_type.vehicle_type_id if vehicle_type else None


class VehicleTypeRepository:  # pylint: disable=R0903
    """Class for vehicle repository operations."""

    @classmethod
    def get_all_vehicle_types(cls):
        """Get all vehicle types from the database."""
        with session_scope() as session:
            vehicle_types = session.query(VehicleType).all()
            return [vehicle_type.to_dict() for vehicle_type in vehicle_types]
    @staticmethod
    @overload
    def get_vehicle_type(vehicle_type_id: int) -> dict:
        pass
    @staticmethod
    @overload
    def get_vehicle_type(vehicle_type_uuid: bytes) -> dict:
        pass
    @staticmethod
    def get_vehicle_type(vehicle_type_id: int = None, vehicle_type_uuid: bytes = None):
        """Get vehicle type by ID or UUID."""
        with session_scope() as session:
            if vehicle_type_id:
                vehicle_type = session.query(VehicleType).filter_by(
                    vehicle_type_id=vehicle_type_id
                ).first()
            else:
                vehicle_type = session.query(VehicleType).filter_by(
                    uuid=vehicle_type_uuid
                ).first()
            return vehicle_type.to_dict() if vehicle_type else None


    @staticmethod
    def create_vehicle_type(vehicle_type_data: dict):
        """Create a new vehicle type."""
        with session_scope() as session:
            vehicle_type = VehicleType(**vehicle_type_data)
            session.add(vehicle_type)
            session.commit()
            return vehicle_type.vehicle_type_id

    @staticmethod
    def update_vehicle_type(vehicle_type_data: dict):
        """Update vehicle type."""
        with session_scope() as session:
            vehicle_type = session.query(VehicleType).filter_by(
                vehicle_type_id = vehicle_type_data["vehicle_type_id"]).update(vehicle_type_data)
            session.commit()
            return vehicle_type.vehicle_type_id
