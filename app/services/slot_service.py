""" This module contains the logic for getting the list of slots. """

from datetime import datetime

from app.exceptions.slot_lookup_exceptions import (
    NoSlotsFoundInTheGivenSlotCode,
    NoSlotsFoundInTheGivenVehicleType,
)
from app.models.company_profile import CompanyProfileRepository
from app.models.parking_establishment import ParkingEstablishment
from app.models.parking_slot import SlotRepository
from app.models.slot import GettingSlotsOperations, SlotOperation


class SlotService:
    """Wraps the logic for getting the list of slots."""

    @staticmethod
    def get_all_slots(establishment_uuid: str):  # pylint: disable=C0116
        return GetSlotService.get_all_slots(establishment_uuid)

    @staticmethod
    def get_slots_by_vehicle_type(
        vehicle_type_id: int, establishment_id: int
    ):  # pylint: disable=C0116
        return GetSlotService.get_slots_by_vehicle_type(
            vehicle_type_id, establishment_id
        )

    @staticmethod
    def get_slot(
        slot_uuid: bytes
    ):  # pylint: disable=C0116
        return GetSlotService.get_slot(slot_uuid)
    
    @staticmethod
    def create_slot(new_slot_data: dict, user_id: int):  # pylint: disable=C0116
        return ParkingManagerService.create_slot(new_slot_data, user_id)
    
    @staticmethod
    def delete_slot(slot_data):
        """Delete a slot."""
        return ParkingManagerService.delete_slot(slot_data)


class GetSlotService:
    """Wraps the logic for getting the list of slots, calling the model layer classes."""
    @staticmethod
    def get_slots(establishment_uuid: bytes):  # pylint: disable=C0116
        establishment_id = ParkingEstablishment.get_establishment_id(
            establishment_uuid
        )
        return SlotRepository.get_slots(establishment_id)  # type: ignore
    
    @staticmethod
    def get_slots_by_vehicle_type(
        vehicle_type_id: int, establishment_id: int
    ):  # pylint: disable=C0116
        slots = GettingSlotsOperations.get_slots_by_vehicle_type(
            vehicle_type_id, establishment_id
        )
        if slots is None:
            raise NoSlotsFoundInTheGivenVehicleType(
                "No slots found in the given vehicle type."
            )
        return slots
    @staticmethod
    def get_slot(slot_uuid: bytes):
        """Get slot by slot code."""
        slot = SlotRepository.get_slot(slot_uuid)
        if slot is None:
            raise NoSlotsFoundInTheGivenSlotCode(
                "No slots found in the given slot code."
            )
        return {"slot_info": slot,}

class ParkingManagerService:  # pylint: disable=R0903
    """Wraps the logic for creating a new slot."""
    @staticmethod
    def create_slot(new_slot_data: dict, user_id):  # pylint: disable=C0116
        manager_id = CompanyProfileRepository.get_company_profile_by_user_id(user_id).get("user_id")
        new_slot_data.update({
            "establishment_id": ParkingEstablishment.get_establishment_id_by_uuid(
                new_slot_data.get("establishment_uuid")
            )
        })
        new_slot_data["created_at"] = datetime.now()
        new_slot_data["updated_at"] = datetime.now()
        return SlotOperation.create_slot(new_slot_data)
    @staticmethod
    def delete_slot(slot_data):
        """Delete a slot."""
        return SlotOperation.delete_slot(slot_data)
