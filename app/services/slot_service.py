""" This module contains the logic for getting the list of slots. """

from app.models.slot import GettingSlotsOperations, CreatingSlotOperations
from app.exceptions.slot_lookup_exceptions import (
    NoSlotsFoundInTheGivenSlotCode,
    NoSlotsFoundInTheGivenEstablishment,
    NoSlotsFoundInTheGivenVehicleType,
)


class SlotService:
    """Wraps the logic for getting the list of slots."""

    @staticmethod
    def get_all_slots():  # pylint: disable=C0116
        return GettingSlotsOperations.get_all_slots()

    @staticmethod
    def get_slots_by_vehicle_type(
        vehicle_type_id: int, establishment_id: int
    ):  # pylint: disable=C0116
        return GetSlotService.get_slots_by_vehicle_type(
            vehicle_type_id, establishment_id
        )

    @staticmethod
    def get_slots_by_establishment_id(establishment_id: int):  # pylint: disable=C0116
        return GetSlotService.get_slots_by_establishment_id(establishment_id)

    @staticmethod
    def get_slots_by_slot_code(slot_code: str):  # pylint: disable=C0116
        return GetSlotService.get_slots_by_slot_code(slot_code)

    @staticmethod
    def create_slot(new_slot_data: dict):  # pylint: disable=C0116
        return CreatingSlotService.create_slot(new_slot_data)


class GetSlotService:
    """Wraps the logic for getting the list of slots, calling the model layer classes."""

    @staticmethod
    def get_all_slots():  # pylint: disable=C0116
        return GettingSlotsOperations().get_all_slots()

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
    def get_slots_by_establishment_id(establishment_id: int):  # pylint: disable=C0116
        slots = GettingSlotsOperations.get_slots_by_establishment(establishment_id)
        if slots is None:
            raise NoSlotsFoundInTheGivenEstablishment(
                "No slots found in the given establishment."
            )
        return slots

    @staticmethod
    def get_slots_by_slot_code(slot_code: str):  # pylint: disable=C0116
        slot = GettingSlotsOperations.get_slots_by_slot_code(slot_code)
        if slot is None:
            raise NoSlotsFoundInTheGivenSlotCode(
                "No slots found in the given slot code."
            )
        return slot


class CreatingSlotService:  # pylint: disable=R0903
    """Wraps the logic for creating a new slot."""

    @staticmethod
    def create_slot(new_slot_data: dict):  # pylint: disable=C0116
        return CreatingSlotOperations.create_slot(new_slot_data)
