""" Class represents parking establishment model in the database. """

from sqlalchemy import (
    VARCHAR, Boolean, Column, Integer, BINARY, TIME, DateTime, DECIMAL,
    func
)
from sqlalchemy.exc import OperationalError

from app.models.base import Base
from app.utils.engine import get_session


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
    longitude = Column(DECIMAL(10, 8), nullable=False)
    latitude = Column(DECIMAL(10, 8), nullable=False)


class GetEstablishmentOperations:
    """ Class for operations related to parking establishment (Getting). """
    @staticmethod
    def get_all_establishments():
        """ Get all parking establishments. """
        session = get_session()
        try:
            establishments = session.query(ParkingEstablishment).all()
            return establishments
        except OperationalError as err:
            raise err


    @staticmethod
    def get_establishment_by_id(establishment_id: int):
        """ Get parking establishment by ID. """
        session = get_session()
        try:
            establishment = session.query(ParkingEstablishment).filter(
                ParkingEstablishment.establishment_id == establishment_id
            ).first()
            return establishment
        except OperationalError as err:
            raise err


    @staticmethod
    def get_nearest_establishments(latitude: float, longitude: float):
        """ Get nearest parking establishments based on the current user location. """
        # Radius of Earth in kilometers
        session = get_session()
        try:
            radius_km = 6371

            establishments = (
                session.query(ParkingEstablishment)
                .filter(
                    ParkingEstablishment.latitude.isnot(None),
                    ParkingEstablishment.longitude.isnot(None)
                )
                .order_by(
                    (
                        radius_km * func.acos(
                            func.cos(func.radians(latitude)) * func.cos(func.radians(ParkingEstablishment.latitude)) *
                            func.cos(func.radians(ParkingEstablishment.longitude) - func.radians(longitude)) +
                            func.sin(func.radians(latitude)) * func.sin(func.radians(ParkingEstablishment.latitude))
                        )
                    ).asc()
                )
            ).all()
            return establishments
        except OperationalError as error:
            raise error

    @staticmethod
    def get_24_hours_establishments():
        """ Get parking establishments that are open 24 hours. """
        session = get_session()
        try:
            establishments = session.query(ParkingEstablishment).filter(
                ParkingEstablishment.is_24_hours == True
            ).all()
            return establishments
        except OperationalError as err:
            raise err
