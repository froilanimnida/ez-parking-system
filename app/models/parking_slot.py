"""
This module contains the SQLAlchemy model for the parking_slot table.
"""


from enum import Enum as PyEnum

from sqlalchemy import (
    Column, Integer, String, Numeric, Boolean, SmallInteger,
    TIMESTAMP, ForeignKey, CheckConstraint, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base


# Enum for slot status
class SlotStatus(PyEnum):
    OPEN = 'open'
    OCCUPIED = 'occupied'
    RESERVED = 'reserved'
    CLOSED = 'closed'


# Enum for slot features
class SlotFeature(PyEnum):
    STANDARD = 'standard'
    PREMIUM = 'premium'


class ParkingSlot(Base):
    __tablename__ = 'parking_slot'
    
    # Columns definition
    slot_id = Column(Integer, primary_key=True, autoincrement=True)
    establishment_id = Column(Integer, ForeignKey('parking_establishment.establishment_id'), nullable=False)
    slot_code = Column(String(45), nullable=False)
    vehicle_type_id = Column(Integer, ForeignKey('vehicle_type.vehicle_type_id'), nullable=False)
    slot_status = Column(ENUM(SlotStatus), nullable=False, default=SlotStatus.OPEN)
    is_active = Column(Boolean, nullable=False, default=True)
    slot_multiplier = Column(Numeric(3, 2), nullable=False, default=1.00)
    floor_level = Column(SmallInteger, nullable=False, default=1)
    base_rate = Column(Numeric(10, 2), default=None)
    is_premium = Column(Boolean, nullable=False, default=False)
    slot_features = Column(ENUM(SlotFeature), nullable=False, default=SlotFeature.STANDARD)
    created_at = Column(TIMESTAMP, default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    __table_args__ = (
        CheckConstraint('base_rate >= 0', name='parking_slot_base_rate_check'),
        CheckConstraint('floor_level <> 0', name='parking_slot_floor_level_check'),
        CheckConstraint('slot_multiplier > 0', name='parking_slot_slot_multiplier_check'),
        UniqueConstraint('establishment_id', 'slot_code', name='unique_establishment_slot_code')
    )
    
    parking_establishment = relationship("ParkingEstablishment", backref="parking_slots")
    vehicle_type = relationship("VehicleType", backref="parking_slots")

    
    def __repr__(self):
        return f"<ParkingSlot(slot_id={self.slot_id}, slot_code={self.slot_code}, status={self.slot_status}, is_active={self.is_active})>"
