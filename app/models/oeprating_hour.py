
from enum import Enum as PyEnum

from sqlalchemy import (
    Column, Integer, Numeric, Boolean, TIMESTAMP, func, ForeignKey, UniqueConstraint, CheckConstraint, String, Time
)
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import relationship

from app.models.base import Base


# Enum for days of the week
class DayOfWeek(PyEnum):
    MONDAY = 'monday'
    TUESDAY = 'tuesday'
    WEDNESDAY = 'wednesday'
    THURSDAY = 'thursday'
    FRIDAY = 'friday'
    SATURDAY = 'saturday'
    SUNDAY = 'sunday'


class OperatingHour(Base):
    __tablename__ = 'operating_hour'
    
    # Columns definition
    hours_id = Column(Integer, primary_key=True, autoincrement=True)
    establishment_id = Column(Integer, ForeignKey('parking_establishment.establishment_id'), nullable=True)
    day_of_week = Column(String(10), nullable=False)
    is_enabled = Column(Boolean, default=False)
    opening_time = Column(Time, nullable=True)
    closing_time = Column(Time, nullable=True)
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('establishment_id', 'day_of_week', name='unique_establishment_day'),
        CheckConstraint(
            "day_of_week IN ('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday')",
            name='operating_hour_day_of_week_check'
        )
    )
    
    # Relationship to ParkingEstablishment
    parking_establishment = relationship("ParkingEstablishment", backref="operating_hours")
    
    def __repr__(self):
        return f"<OperatingHour(hours_id={self.hours_id}, establishment_id={self.establishment_id}, day_of_week={self.day_of_week})>"
