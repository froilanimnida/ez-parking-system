"""This module defines the OperatingHour model."""

from datetime import time
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
            'day_of_week': self.day_of_week.title(),
            'is_enabled': self.is_enabled,
            'opening_time': self.opening_time.isoformat() if self.opening_time else None,
            'closing_time': self.closing_time.isoformat() if self.closing_time else None
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

    @staticmethod
    def update_operating_hours(establishment_id, operating_hours: dict):
        """
        Update operating hours for a parking establishment.
    
        Args:
            establishment_id: ID of the establishment
            operating_hours: Dictionary of operating hours with format:
                {
                    'monday': {'enabled': bool, 'open': str, 'close': str},
                    'tuesday': {'enabled': bool, 'open': str, 'close': str},
                    ...
                }
        """
        with session_scope() as session:
            existing_hours = session.query(OperatingHour).filter_by(
                establishment_id=establishment_id
            ).all()
    
            for day, hours in operating_hours.items():
                operating_hour = next(
                    (h for h in existing_hours if h.day_of_week == day.lower()),
                    None
                )
    
                if not operating_hour:
                    operating_hour = OperatingHour(
                        establishment_id=establishment_id,
                        day_of_week=day.lower()
                    )
                    session.add(operating_hour)
    
                operating_hour.is_enabled = hours.get('enabled', False)
    
                opening_time = hours.get('open')
                if opening_time:
                    if isinstance(opening_time, str):
                        hour, minute = map(int, opening_time.split(':')[:2])
                        operating_hour.opening_time = time(hour, minute)
                    elif isinstance(opening_time, time):
                        operating_hour.opening_time = opening_time
    
                closing_time = hours.get('close')
                if closing_time:
                    if isinstance(closing_time, str):
                        hour, minute = map(int, closing_time.split(':')[:2])
                        operating_hour.closing_time = time(hour, minute)
                    elif isinstance(closing_time, time):
                        operating_hour.closing_time = closing_time
    @staticmethod
    def make_operating_hours_24_7(establishment_id):
        """
            Make operating hours 24/7 for a parking establishment.
            Sets all days to enabled with 00:00 opening time and 23:59 closing time.
        """
        with session_scope() as session:
            existing_hours = session.query(
                OperatingHour).filter_by(
                    establishment_id=establishment_id
                    ).all()

            for day in DayOfWeek:
                existing_entry = next(
                    (hour for hour in existing_hours if hour.day_of_week == day.value),
                    None
                )

                if existing_entry:
                    existing_entry.is_enabled = True
                    existing_entry.opening_time = time(0, 0)
                    existing_entry.closing_time = time(23, 59)
                else:
                    new_entry = OperatingHour(
                        establishment_id=establishment_id,
                        day_of_week=day.value,
                        is_enabled=True,
                        opening_time=time(0, 0),
                        closing_time=time(23, 59)
                    )
                    session.add(new_entry)
