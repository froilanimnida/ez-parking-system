"""
This module contains the SQLAlchemy model for the parking_slot table.
"""

# pylint: disable=E1102, C0103:

from enum import Enum as PyEnum
from typing import Any, overload, Literal

from sqlalchemy import (
    Column, Integer, String, Numeric, Boolean, SmallInteger, TIMESTAMP, ForeignKey, CheckConstraint,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.exceptions.slot_lookup_exceptions import SlotNotFound
from app.models.base import Base
from app.models.vehicle_type import VehicleType
from app.utils.db import session_scope


# Enum for slot status
class SlotStatus(PyEnum):
    """Encapsulate enumerate types of slot status."""
    open = "open"
    occupied = "occupied"
    reserved = "reserved"
    closed = "closed"


# Enum for slot features
class SlotFeature(PyEnum):
    """Encapsulate enumerate types of slot features."""
    standard = "standard"
    covered = "covered"
    vip = "vip"
    disabled = "disabled"
    ev_charging = "ev_charging"

class ParkingSlot(Base):  # pylint: disable=too-few-public-methods
    """Define the parking_slot table model."""
    __tablename__ = "parking_slot"

    slot_id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False, default=func.uuid_generate_v4())
    establishment_id = Column(
        Integer, ForeignKey("parking_establishment.establishment_id"), nullable=False
    )
    slot_code = Column(String(45), nullable=False)
    vehicle_type_id = Column(Integer, ForeignKey("vehicle_type.vehicle_type_id"), nullable=False)
    slot_status = Column(ENUM(SlotStatus), nullable=False, default=SlotStatus.open)
    is_active = Column(Boolean, nullable=False, default=True)
    slot_multiplier = Column(Numeric(3, 2), nullable=False, default=1.00) # TODO: Remove this for consolidation of pricing to per-slot based
    floor_level = Column(SmallInteger, nullable=False, default=1)
    base_rate = Column(Numeric(10, 2), default=None) # TODO: Remove this for consolidation of pricing to per-slot based
    is_premium = Column(Boolean, nullable=False, default=False)
    slot_features = Column(ENUM(SlotFeature), nullable=False, default=SlotFeature.standard)
    # TODO: New pricing fields
    # base_price_per_hour DECIMAL(10,2) NOT NULL,
    # base_price_per_day DECIMAL(10,2) NOT NULL,
    # base_price_per_month DECIMAL(10,2) NOT NULL,
    # price_multiplier DECIMAL(3,2) NOT NULL DEFAULT 1.00,
    created_at = Column(TIMESTAMP, default=func.current_timestamp())
    updated_at = Column(
        TIMESTAMP, default=func.current_timestamp(), onupdate=func.current_timestamp()
    )

    __table_args__ = (
        CheckConstraint("base_rate >= 0", name="parking_slot_base_rate_check"),
        CheckConstraint("floor_level <> 0", name="parking_slot_floor_level_check"),
        CheckConstraint(
            "slot_multiplier > 0", name="parking_slot_slot_multiplier_check"
        ),
        UniqueConstraint(
            "establishment_id", "slot_code", name="unique_establishment_slot_code"
        ),
    )

    parking_establishment = relationship("ParkingEstablishment", back_populates="parking_slots")
    vehicle_type = relationship("VehicleType", back_populates="parking_slots")
    transactions = relationship("ParkingTransaction", back_populates="parking_slots")

    def to_dict(self):
        """
        Return the parking slot object as a dictionary.
        """
        if self is None:
            return {}
        return {
            "slot_id": self.slot_id,
            "uuid": str(self.uuid),
            "establishment_id": self.establishment_id,
            "slot_code": self.slot_code,
            "vehicle_type_id": self.vehicle_type_id,
            "slot_status": self.slot_status.value if self.slot_status else None,
            "is_active": self.is_active,
            "slot_multiplier": str(self.slot_multiplier),
            "floor_level": self.floor_level,
            "base_rate": str(self.base_rate),
            "is_premium": self.is_premium,
            "slot_features": self.slot_features.value if self.slot_features else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    @staticmethod
    def get_id(uuid: str) -> int:
        """Get the ID of the parking slot."""
        with session_scope() as session:
            slot = session.query(ParkingSlot).filter_by(uuid=uuid).first()
            if slot:
                return slot.slot_id
            raise SlotNotFound("Slot not found")


    # def calculate_total_multiplier(self) -> float:
    #     """Calculate final rate multiplier including vehicle type and slot factors"""
    #     base_multiplier = float(self.vehicle_type.base_rate_multiplier)
    #     slot_multiplier = float(self.slot_multiplier)  # type: ignore
    #
    #     # Additional multipliers based on features
    #     feature_multipliers = {"covered": 1.2, "vip": 1.5, "ev_charging": 1.3}
    #
    #     feature_mult = feature_multipliers.get(self.slot_features, 1.0)  # type: ignore
    #
    #     return base_multiplier * slot_multiplier * feature_mult


class ParkingSlotRepository:
    """Repository for ParkingSlot model."""
    @staticmethod
    def create_slot(slot_data: dict) -> int:
        """
        Create a new parking slot.

        Parameters:
            slot_data (dict): Dictionary containing slot details.

        Returns:
            int: The ID of the newly created slot.
        """
        with session_scope() as session:
            new_slot = ParkingSlot(**slot_data)
            session.add(new_slot)
            session.flush()
            session.refresh(new_slot)
            return new_slot.slot_id

    @staticmethod
    @overload
    def get_slot(slot_code: str) -> dict:
        """
        Get a parking slot by slot code.

        Parameters:
            slot_code (str): The code of the slot.

        Returns:
            dict: The parking slot object.
        """

    @staticmethod
    @overload
    def get_slot(slot_uuid: str) -> dict:
        """
        Get a parking slot by slot code and establishment ID.

        Parameters:
            slot_uuid (str): The UUID of the slot.

        Returns:
            dict: The parking slot object.
        """

    @staticmethod
    @overload
    def get_slot(slot_id: int) -> dict:
        """
        Get a parking slot by slot ID.

        Parameters:
            slot_id (int): The ID of the slot.

        Returns:
            dict: The parking slot object.
        """

    @staticmethod
    def get_slot(slot_code: str = None, slot_uuid: str = None, slot_id: int = None) -> dict:
        """
        Get a parking slot by slot code, establishment ID, or slot ID.

        Parameters:
            slot_code (str): The code of the slot.
            slot_uuid (str): The UUID of the slot.
            slot_id (int): The ID of the slot.

        Returns:
            dict: The parking slot object.
        """
        with session_scope() as session:
            slot = None
            print(slot_code)
            if slot_code:
                slot = session.query(ParkingSlot).filter_by(slot_code=slot_code).join(
                    VehicleType,
                    ParkingSlot.vehicle_type_id == VehicleType.vehicle_type_id
                ).first()
            if slot_uuid:
                slot = session.query(ParkingSlot).filter_by(uuid=slot_uuid).join(
                    VehicleType,
                    ParkingSlot.vehicle_type_id == VehicleType.vehicle_type_id
                ).first()
            if slot_id:
                slot = session.query(ParkingSlot).filter_by(slot_id=slot_id).join(
                    VehicleType,
                    ParkingSlot.vehicle_type_id == VehicleType.vehicle_type_id
                ).first()
            if slot:
                slot_dict = slot.to_dict()
                slot_dict.update({
                    "vehicle_type_name": slot.vehicle_type.name,
                    "vehicle_type_code": slot.vehicle_type.code,
                    "vehicle_type_size": slot.vehicle_type.size_category.value
                })
                return slot_dict
            return {}


    @staticmethod
    def delete_slot(slot_uuid: bytes) -> int:
        """
        Delete a parking slot.

        Parameters:
            slot_uuid (bytes): The UUID of the slot to be deleted.

        Returns:
            int: The ID of the deleted slot.
        """
        with session_scope() as session:
            slot = session.query(ParkingSlot).get(slot_uuid)
            if slot:
                session.delete(slot)
                return slot.slot_id
            raise SlotNotFound("Slot not found")

    @staticmethod
    def update_slot(slot_data: dict) -> int:
        """
        Update a parking slot by the uuid of the slot.

        Parameters:
            slot_data (dict): Dictionary containing updated slot details.

        Returns:
            int: The ID of the updated slot.
        """
        with session_scope() as session:
            result = session.query(ParkingSlot).filter(
                ParkingSlot.uuid == slot_data.get("uuid")
            ).update(slot_data)
            if result:
                return result
            raise SlotNotFound("Slot not found")


    @staticmethod
    @overload
    def get_slots(establishment_id: int = None):
        """
        Get all parking slots by establishment ID.

        Parameters:
            establishment_id (int): The ID of the establishment.

        Returns:
            list: List of parking slot objects.
        """
    @staticmethod
    @overload
    def get_slots():
        """
        Get all parking slots.

        Returns:
            list: List of parking slot objects.
        """
    @staticmethod
    def get_slots(establishment_id: int = None) -> list[dict[str, Any]]:
        """
        Get all parking slots by establishment ID or all slots.

        Parameters:
            establishment_id (int): The ID of the establishment.

        Returns:
            list: List of parking slot objects.
        """
        with session_scope() as session:
            if establishment_id:
                query = session.query(
                    ParkingSlot,
                    VehicleType.name.label("vehicle_type_name"),
                    VehicleType.code.label("vehicle_type_code"),
                    VehicleType.size_category.label("vehicle_type_size"),
                ).filter_by(establishment_id=establishment_id).join(
                    VehicleType,ParkingSlot.vehicle_type_id == VehicleType.vehicle_type_id
                ).all()
            else:
                query = session.query(ParkingSlot).all()
            slots = []
            for slot, vehicle_type_name, vehicle_type_code, vehicle_type_size in query:
                slot_dict = slot.to_dict()
                slot_dict.update({
                    "vehicle_type_name": vehicle_type_name,
                    "vehicle_type_code": vehicle_type_code,
                    "vehicle_type_size": vehicle_type_size.value
                })
                slot_dict.pop("vehicle_type_id")
                slots.append(slot_dict)
            return slots
    @staticmethod
    @overload
    def change_slot_status(
        slot_id: int, new_status: Literal["open", "occupied", "reserved", "closed"]
    ) -> int: ...
    @staticmethod
    @overload
    def change_slot_status(
        slot_uuid: str, new_status: Literal["open", "occupied", "reserved", "closed"]
    ) -> int: ...
    @staticmethod
    def change_slot_status(
        slot_uuid: str = None, slot_id: int = None,
        new_status: Literal["open", "occupied", "reserved", "closed"] = "open"
    ) -> int:
        """
        Change the status of a parking slot.

        Parameters:
            slot_uuid (str): The UUID of the slot.
            slot_id (int): The ID of the slot.
            new_status (SlotStatus): The new status of the slot.

        Returns:
            int: The ID of the updated slot.
        """
        with session_scope() as session:
            slot = None
            if slot_uuid:
                slot = session.query(ParkingSlot).filter_by(uuid=slot_uuid).first()
            if slot_id:
                slot = session.query(ParkingSlot).filter_by(slot_id=slot_id).first()
            if slot:
                slot.slot_status = new_status
                return slot.slot_id
            raise SlotNotFound("Slot not found")
