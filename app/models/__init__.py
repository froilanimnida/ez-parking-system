""" Initialized all the models in the database. """

from app.models.audit import Audit
from app.models.banned_plate import BannedPlate
from app.models.parking_establishment import ParkingEstablishment
from app.models.parking_transaction import ParkingTransaction
from app.models.slot import Slot
from app.models.user import User
from app.models.vehicle_type import VehicleType
from app.models.parking_manager_file import ParkingManagerFile

__all__ = [
    "User",
    "ParkingEstablishment",
    "Slot",
    "VehicleType",
    "ParkingTransaction",
    "BannedPlate",
    "Audit",
    "ParkingManagerFile",
]
