""" All routes related to slot retrieval, creation, and deletion. """

# pylint: disable=missing-function-docstring, missing-class-docstring

from flask_smorest import Blueprint
from flask.views import MethodView
from flask_jwt_extended import jwt_required

from app.schema.query_validation import (
    EstablishmentQueryValidation,
    EstablishmentSlotTypeValidation,
    SlotCodeValidationQuerySchema,
)
from app.schema.response_schema import ApiResponse
from app.exceptions.slot_lookup_exceptions import (
    NoSlotsFoundInTheGivenSlotCode,
    NoSlotsFoundInTheGivenEstablishment,
    NoSlotsFoundInTheGivenVehicleType,
)
from app.exceptions.vehicle_type_exceptions import VehicleTypeDoesNotExist
from app.services.slot_service import SlotService
from app.utils.response_util import set_response
from app.utils.error_handlers.vehicle_type_error_handlers import (
    handle_vehicle_type_does_not_exist,
)
from app.utils.error_handlers.slot_lookup_error_handlers import (
    handle_no_slots_found_in_the_given_slot_code,
    handle_no_slots_found_in_the_given_establishment,
    handle_no_slots_found_in_the_given_vehicle_type,
)

slot_blp = Blueprint(
    "slot",
    __name__,
    url_prefix="/api/v1/slot",
    description="Slot API for EZ Parking System Frontend",
)


@slot_blp.route("/get-all-slots")
class GetSlotsByEstablishmentID(MethodView):

    @slot_blp.arguments(EstablishmentQueryValidation)
    @slot_blp.response(200, ApiResponse)
    @slot_blp.doc(
        description="Get all slots by establishment uuid",
        responses={
            200: {"description": "Slots retrieved successfully"},
            400: {"description": "Bad Request"},
        },
    )
    @jwt_required(True)
    def get(self, data):
        slots = SlotService.get_all_slots(data.get("establishment_uuid"))
        return set_response(200, {"slots": slots})


@slot_blp.route("/get-slots-by-vehicle-type")
class GetSlotsByVehicleType(MethodView):
    """Get slots by vehicle type."""

    @slot_blp.arguments(EstablishmentSlotTypeValidation)
    @slot_blp.response(200, ApiResponse)
    @slot_blp.doc(
        description="Get all slots by vehicle type",
        responses={
            200: {"description": "Slots retrieved successfully"},
            400: {"description": "Bad Request"},
        },
    )
    @jwt_required(True)
    def get(self, data):
        vehicle_size = data.get("vehicle_size")
        establishment_id = data.get("establishment_id")
        slots = SlotService.get_slots_by_vehicle_type(vehicle_size, establishment_id)
        return set_response(200, {"slots": slots})


@slot_blp.route("/get-slots-by-slot-code")
class GetSlotsBySlotCode(MethodView):
    """Get slots by slot code."""

    @slot_blp.arguments(SlotCodeValidationQuerySchema)
    @slot_blp.response(200, ApiResponse)
    @slot_blp.doc(
        description="Get all slots by slot code",
        responses={
            200: {"description": "Slots retrieved successfully"},
            400: {"description": "Bad Request"},
        },
    )
    @jwt_required(True)
    def get(self, data):
        slot_code = data.get("slot_code")
        slots = SlotService.get_slots_by_slot_code(slot_code)
        return set_response(200, {"slots": slots})


slot_blp.register_error_handler(
    NoSlotsFoundInTheGivenSlotCode, handle_no_slots_found_in_the_given_slot_code
)
slot_blp.register_error_handler(
    NoSlotsFoundInTheGivenEstablishment,
    handle_no_slots_found_in_the_given_establishment,
)
slot_blp.register_error_handler(
    NoSlotsFoundInTheGivenVehicleType, handle_no_slots_found_in_the_given_vehicle_type
)
slot_blp.register_error_handler(
    VehicleTypeDoesNotExist, handle_vehicle_type_does_not_exist
)
