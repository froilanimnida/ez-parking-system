""" All routes related to slot retrieval, creation, and deletion. """

from flask import Blueprint, request

from app.schema.slot_validation import SlotValidationSchema
from app.exceptions.slot_lookup_exceptions import (
    NoSlotsFoundInTheGivenSlotCode,
    NoSlotsFoundInTheGivenEstablishment,
    NoSlotsFoundInTheGivenVehicleType,
)
from app.exceptions.vehicle_type_exceptions import VehicleTypeDoesNotExist
from app.services.slot_service import SlotService
from app.utils.response_util import set_response
from app.utils.error_handlers import (
    handle_no_slots_found_in_the_given_slot_code,
    handle_no_slots_found_in_the_given_establishment,
    handle_no_slots_found_in_the_given_vehicle_type,
    handle_vehicle_type_does_not_exist,
)

slot = Blueprint("slot", __name__)

slot.register_error_handler(
    NoSlotsFoundInTheGivenSlotCode, handle_no_slots_found_in_the_given_slot_code
)
slot.register_error_handler(
    NoSlotsFoundInTheGivenEstablishment,
    handle_no_slots_found_in_the_given_establishment,
)
slot.register_error_handler(
    NoSlotsFoundInTheGivenVehicleType, handle_no_slots_found_in_the_given_vehicle_type
)
slot.register_error_handler(VehicleTypeDoesNotExist, handle_vehicle_type_does_not_exist)


@slot.route("/v1/slot/get-all-slots", methods=["GET"])
def get_all_slots():
    """Get all slots."""
    slots = SlotService.get_all_slots()
    data = slots
    response = set_response(200, "Slots retrieved successfully.")
    response.data = data
    return response


@slot.route("/v1/slot/get-slots-by-vehicle-type/", methods=["GET"])
def get_slots_by_vehicle_type():
    """Get slots by vehicle type."""
    data = request.get_json()
    if not data:
        return set_response(400, "Please provide vehicle type and establishment ID.")
    vehicle_type_id = data.get("vehicle_type_id")
    establishment_id = data.get("establishment_id")
    slots = SlotService.get_slots_by_vehicle_type(vehicle_type_id, establishment_id)
    data = slots
    response = set_response(200, "Slots retrieved successfully.")
    response.data = data
    return response


@slot.route("/v1/slot/get-slots-by-establishment-id/", methods=["GET"])
def get_slots_by_establishment_id():
    """Get slots by establishment ID."""
    data = request.get_json()
    if not data:
        return set_response(400, "Please provide establishment ID.")
    establishment_id = data.get("establishment_id")
    slots = SlotService.get_slots_by_establishment_id(establishment_id)
    data = slots
    response = set_response(200, "Slots retrieved successfully.")
    response.data = data
    return response


@slot.route("/v1/slot/get-slots-by-slot-code/", methods=["GET"])
def get_slots_by_slot_code():
    """Get slots by slot code."""
    data = request.get_json()
    if not data:
        return set_response(400, "Please provide slot code.")
    slot_code = data.get("slot_code")
    slots = SlotService.get_slots_by_slot_code(slot_code)
    data = slots
    response = set_response(200, "Slots retrieved successfully.")
    response.data = data
    return response


@slot.route("/v1/slots/create", methods=["POST"])
def create_slot():
    """Create a new slot."""
    data = request.get_json()
    if not data:
        return set_response(400, "Please provide slot data.")
    slot_validation_schema = SlotValidationSchema()
    new_slot_data = slot_validation_schema.load(data)
    SlotService.create_slot(new_slot_data)  # type: ignore
    return set_response(201, "Slot created successfully.")
