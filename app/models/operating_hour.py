"""This module defines the OperatingHour model."""

from enum import Enum as PyEnum

from sqlalchemy import (
    Column, Integer, Boolean, ForeignKey, UniqueConstraint, CheckConstraint, String, Time
)
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.utils.db import session_scope


# Enum for days of the week
class DayOfWeek(PyEnum):
    """Encapsulate enumerate types of days of the week."""
    MONDAY = 'monday'
    TUESDAY = 'tuesday'
    WEDNESDAY = 'wednesday'
    THURSDAY = 'thursday'
    FRIDAY = 'friday'
    SATURDAY = 'saturday'
    SUNDAY = 'sunday'

class OperatingHour(Base):  # pylint: disable=too-few-public-methods
    """OperatingHour model."""
    __tablename__ = 'operating_hour'

    hours_id = Column(Integer, primary_key=True, autoincrement=True)
    establishment_id = Column(
        Integer,
        ForeignKey('parking_establishment.establishment_id'),
        nullable=True
    )
    day_of_week = Column(String(10), nullable=False)
    is_enabled = Column(Boolean, default=False)
    opening_time = Column(Time, nullable=True)
    closing_time = Column(Time, nullable=True)

    __table_args__ = (
        UniqueConstraint('establishment_id', 'day_of_week', name='unique_establishment_day'),
        CheckConstraint(
            """day_of_week IN ('monday', 'tuesday',
            'wednesday', 'thursday', 'friday', 'saturday', 'sunday')""",
            name='operating_hour_day_of_week_check'
        )
    )

    parking_establishment = relationship("ParkingEstablishment", back_populates="operating_hours")

    def to_dict(self):
        """Convert model to dictionary."""
        if self is None:
            return {}
        return {
            'hours_id': self.hours_id,
            'establishment_id': self.establishment_id,
            'day_of_week': self.day_of_week,
            'is_enabled': self.is_enabled,
            'opening_time': self.opening_time,
            'closing_time': self.closing_time
        }


class OperatingHoursRepository:
    """Repository for OperatingHour model."""

    @staticmethod
    def get_operating_hours(establishment_id):
        """Get operating hours of a parking establishment."""
        with session_scope() as session:
            operating_hours = session.query(
                OperatingHour).filter_by(establishment_id=establishment_id).all()
            return [hour.to_dict() for hour in operating_hours]

    @staticmethod
    def create_operating_hours(establishment_id, operating_hours: dict):
        """Create operating hours for a parking establishment."""
        with session_scope() as session:
            for day, hours in operating_hours.items():
                operating_hour = OperatingHour(
                    establishment_id=establishment_id,
                    day_of_week=day,
                    is_enabled=hours.get('is_enabled'),
                    opening_time=hours.get('opening_time'),
                    closing_time=hours.get('closing_time')
                )
                session.add(operating_hour)
            session.commit()

    @staticmethod
    def update_operating_hours(establishment_id, operating_hours: dict):
        """Update operating hours for a parking establishment."""
        with session_scope() as session:
            for day, hours in operating_hours.items():
                operating_hour = session.query(OperatingHour).filter_by(
                    establishment_id=establishment_id, day_of_week=day
                ).first()
                operating_hour.is_enabled = hours.get('is_enabled')
                operating_hour.opening_time = hours.get('opening_time')
                operating_hour.closing_time = hours.get('closing_time')
            session.commit()
