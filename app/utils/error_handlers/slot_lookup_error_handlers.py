""" Wraps the error handlers for the slot lookup related errors. """

from app.exceptions.slot_lookup_exceptions import (
    NoSlotsFoundInTheGivenSlotCode, NoSlotsFoundInTheGivenEstablishment,
    NoSlotsFoundInTheGivenVehicleType, SlotNotFound, SlotStatusTaken, SlotAlreadyExists
)
from app.utils.error_handlers.base_error_handler import handle_error


def handle_no_slots_found_in_the_given_vehicle_type(error):
    """This function handles no slots found in the given vehicle type exceptions."""
    if isinstance(error, NoSlotsFoundInTheGivenVehicleType):
        return handle_error(
            error,
            404,
            "no_slots_found_in_the_given_vehicle_type",
            "No slots found in the given vehicle type.",
        )
    raise error


def handle_no_slots_found_in_the_given_slot_code(error):
    """This function handles no slots found in the given slot code exceptions."""
    if isinstance(error, NoSlotsFoundInTheGivenSlotCode):
        return handle_error(
            error,
            404,
            "no_slots_found_in_the_given_slot_code",
            "No slots found in the given slot code.",
        )
    raise error


def handle_no_slots_found_in_the_given_establishment(error):
    """This function handles no slots found in the given establishment exceptions."""
    if isinstance(error, NoSlotsFoundInTheGivenEstablishment):
        return handle_error(
            error,
            404,
            "no_slots_found_in_the_given_establishment",
            "No slots found in the given establishment.",
        )
    raise error


def handle_slot_not_found(error):
    """This function handles slot not found exceptions."""
    if isinstance(error, SlotNotFound):
        return handle_error(
            error,
            404,
            "slot_not_found",
            "Slot not found.",
        )
    raise error


def handle_slot_taken(error):
    """This function handles slot taken exceptions."""
    if isinstance(error, SlotStatusTaken):
        return handle_error(
            error,
            400,
            "slot_status_taken",
            "Slot status is taken.",
        )
    return error

def handle_slot_already_exists(error):
    """This function handles slot already exists exceptions."""
    if isinstance(error, SlotAlreadyExists):
        return handle_error(
            error,
            400,
            "slot_already_exists",
            "Slot code already exists.",
        )
    return error
