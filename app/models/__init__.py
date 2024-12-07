""" Initialized all the models in the database. """

from app.models.audit import Audit
from app.models.banned_plate import BannedPlate
from app.models.parking_establishment import ParkingEstablishment
from app.models.parking_transaction import ParkingTransaction
from app.models.user import User
from app.models.vehicle_type import VehicleType
from app.models.parking_manager_file import ParkingManagerFile
from app.models.company_profile import CompanyProfile
from app.models.address import Address
from app.models.parking_slot import ParkingSlot

__all__ = [
    "User",
    "ParkingEstablishment",
    "ParkingSlot",
    "VehicleType",
    "ParkingTransaction",
    "BannedPlate",
    "Audit",
    "ParkingManagerFile",
    "CompanyProfile",
    "Address",
]
