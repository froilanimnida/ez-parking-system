""" Class model represents the model for the slot in the database. """

from sqlalchemy import (
    Column, Integer, VARCHAR, Enum, DateTime, ForeignKey, Boolean,
)
from sqlalchemy.orm import relationship
from sqlalchemy.exc import OperationalError

from app.models.base import Base
from app.utils.engine import get_session

class Slot(Base):
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


class GettingSlotsOperations:  # pylint: disable=R0903
    """ Wraps the logic for getting the list of slots. """
    @staticmethod
    def get_all_slots():
        """ Get all slots. This is for administrative purposes. """
        session = get_session()
        try:
            slots = session.query(Slot).all()
            return slots
        except OperationalError as error:
            raise error

    @staticmethod
    def get_slot_by_vehicle_type(vehicle_type_id: int, establishment_id: int):  # pylint: disable=C0116
        session = get_session()
        try:
            slots = session.query(Slot).filter(
                Slot.vehicle_type_id == vehicle_type_id,
                Slot.establishment_id == establishment_id
            ).all()
            return slots
        except OperationalError as error:
            raise error


    @staticmethod
    def get_slot_by_establishment(establishment_id: int):  # pylint: disable=C0116
        session = get_session()
        try:
            slots = session.query(Slot).filter(
                Slot.establishment_id == establishment_id
            ).all()
            return slots
        except OperationalError as error:
            raise error

    @staticmethod
    def get_slot_by_slot_code(slot_code: str): # pylint: disable=C0116
        session = get_session()
        try:
            slot = session.query(Slot).filter(
                Slot.slot_code == slot_code
            ).first()
            return slot
        except OperationalError as error:
            raise error
