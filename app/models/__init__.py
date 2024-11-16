""" Initialized all the models in the database. """

from app.models.user import User
from app.models.parking_establishment import ParkingEstablishment
from app.models.slot import Slot
from app.models.vehicle_type import VehicleType
from app.models.parking_transaction import ParkingTransaction

__all__ = ["User", "ParkingEstablishment", "Slot", "VehicleType", "ParkingTransaction"]
