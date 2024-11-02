""" Class represents parking establishment model in the database. """

from sqlalchemy import (
    VARCHAR, Boolean, Column, Integer, BINARY, TIME, DateTime, DECIMAL
)

from app.models.base import Base


class ParkingEstablishment(Base):
    """ Class represents parking establishment model in the database. """

    __tablename__ = 'parking_establishment'

    establishment_id = Column(Integer, primary_key=True)
    uuid = Column(BINARY(16), nullable=False)
    name = Column(VARCHAR(255), nullable=False)
    address = Column(VARCHAR(255), nullable=False)
    contact_number = Column(VARCHAR(25), nullable=False)
    opening_time = Column(TIME, nullable=False)
    closing_time = Column(TIME, nullable=False)
    is_24_hours = Column(Boolean, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    hourly_rate = Column(DECIMAL(8, 2), nullable=False)
