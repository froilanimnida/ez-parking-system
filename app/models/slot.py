""" Class model represents the model for the slot in the database. """

from sqlalchemy import (
    Column, Integer, VARCHAR, Enum, DateTime, ForeignKey, Boolean,
)
from sqlalchemy.orm import relationship

from app.models.base import Base

class SlotModel(Base):
    """ Class model represents the model for the slot in the database. """
    __tablename__ = 'slot'

    slot_id = Column(Integer, primary_key=True)
    establishment_id = Column(
        Integer,
        ForeignKey('parking_establishment.establishment_id'),
        nullable=False
    )
    slot_code = Column(VARCHAR(45), nullable=False)
    vehicle_type_id = Column(
        Integer,
        ForeignKey('vehicle_type.vehicle_id'),
    )
    slot_status = Column(
        Enum('open', 'reserved', 'occupied'),
        nullable=False,
        default='open'
    )
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    vehicle_type = relationship(
        'VehicleType',
        back_populates='slots',
        cascade='all, delete-orphan'
    )
    parking_establishment = relationship(
        'ParkingEstablishment',
        back_populates='slots',
        cascade='all, delete-orphan'
    )
