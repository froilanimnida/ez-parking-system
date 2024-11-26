""" This module contains the logic for getting the list of slots. """

from datetime import datetime

from app.models.parking_establishment import ParkingEstablishment
from app.models.slot import GettingSlotsOperations, SlotOperation
from app.exceptions.slot_lookup_exceptions import (
    NoSlotsFoundInTheGivenSlotCode,
    NoSlotsFoundInTheGivenVehicleType,
)
from ..utils.uuid_utility import UUIDUtility


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
    def get_slot_by_slot_code(
        slot_code: str, establishment_uuid
    ):  # pylint: disable=C0116
        return GetSlotService.get_slot_by_slot_code(slot_code, establishment_uuid)

    @staticmethod
    def create_slot(new_slot_data: dict):  # pylint: disable=C0116
        return ParkingManagerService.create_slot(new_slot_data)

    @staticmethod
    def get_specific_slot(slot_code: str):
        """Get specific slot by slot code."""
        return GetSlotService.get_specific_slot(slot_code)


class GetSlotService:
    """Wraps the logic for getting the list of slots, calling the model layer classes."""

    @staticmethod
    def get_all_slots(establishment_uuid: str):  # pylint: disable=C0116
        establishment_uuid_bytes = establishment_uuid.encode("utf-8")
        establishment_id = ParkingEstablishment.get_establishment_id_by_uuid(
            establishment_uuid_bytes
        )
        return GettingSlotsOperations.get_all_slots(establishment_id)  # type: ignore

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
    def get_slot_by_slot_code(
        slot_code: str, establishment_uuid: str
    ):  # pylint: disable=C0116
        uuid_utility = UUIDUtility()
        establishment_uuid_binary = uuid_utility.uuid_to_binary(establishment_uuid)
        establishment_id = ParkingEstablishment.get_establishment_id_by_uuid(
            establishment_uuid_binary
        )
        slot = GettingSlotsOperations.get_slot_by_slot_code(
            slot_code, establishment_id  # type: ignore
        )
        if slot is None:
            raise NoSlotsFoundInTheGivenSlotCode(
                "No slots found in the given slot code."
            )
        return slot

    @staticmethod
    def get_specific_slot(slot_code: str):  # pylint: disable=C0116
        pass


class ParkingManagerService:  # pylint: disable=R0903
    """Wraps the logic for creating a new slot."""

    @staticmethod
    def create_slot(new_slot_data: dict):  # pylint: disable=C0116
        new_slot_data["created_at"] = datetime.now()
        new_slot_data["updated_at"] = datetime.now()
        return SlotOperation.create_slot(new_slot_data)
