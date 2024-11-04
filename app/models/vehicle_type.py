""" Model represents the vehicle type in the database. """

from sqlalchemy import (
    Column, Integer, VARCHAR, Enum, DECIMAL, DateTime
)
from sqlalchemy.orm import relationship

from app.models.base import Base


class VehicleType(Base):  # pylint: disable=R0903
    """ Model represents the vehicle type in the database. """
    __tablename__ = 'vehicle_type'

    vehicle_id = Column(Integer, primary_key=True)
    name = Column(VARCHAR(125), nullable=False)
    description = Column(VARCHAR(255), nullable=False)
    size_category = Column(
        Enum('Motorcycle', 'Compact', 'Sedan', 'SUV', 'Truck', 'Oversized'),
        nullable=False
    )
    rate_multiplier = Column(DECIMAL(3, 2), nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    slot = relationship(
        'Slot',
        back_populates='vehicle_type',
        cascade='all, delete-orphan'
    )
