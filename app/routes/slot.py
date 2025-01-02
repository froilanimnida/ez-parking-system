""" All routes related to slot retrieval, creation, and deletion. """

# pylint: disable=missing-function-docstring, missing-class-docstring

from flask import request
from flask.views import MethodView
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint

from app.exceptions.slot_lookup_exceptions import (
    NoSlotsFoundInTheGivenSlotCode, NoSlotsFoundInTheGivenEstablishment,
    NoSlotsFoundInTheGivenVehicleType, SlotAlreadyExists,
)
from app.exceptions.vehicle_type_exceptions import VehicleTypeDoesNotExist
from app.utils.role_decorator import parking_manager_role_required
from app.schema.parking_manager_validation import (
    CreateSlotSchema, DeleteSlotSchemaSchema, UpdateSlotSchemaSchema
)
from app.schema.query_validation import EstablishmentQueryValidationSchema
from app.schema.response_schema import ApiResponse
from app.services.slot_service import ParkingSlotService
from app.utils.error_handlers.slot_lookup_error_handlers import (
    handle_no_slots_found_in_the_given_slot_code, handle_no_slots_found_in_the_given_establishment,
    handle_no_slots_found_in_the_given_vehicle_type, handle_slot_already_exists,
)
from app.utils.error_handlers.vehicle_type_error_handlers import handle_vehicle_type_does_not_exist
from app.utils.response_util import set_response

slot_blp = Blueprint(
    "slot",
    __name__,
    url_prefix="/api/v1/slot",
    description="Slot API for EZ Parking System Frontend",
)


@slot_blp.route("/get-all-slots")
class GetSlotsByEstablishmentID(MethodView):
    @slot_blp.arguments(EstablishmentQueryValidationSchema)
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
        slots = ParkingSlotService.get_all_slots(data.get("establishment_uuid"))
        return set_response(200, {"slots": slots})


@slot_blp.route("/create")
class CreateSlot(MethodView):
    @slot_blp.arguments(CreateSlotSchema)
    @slot_blp.response(201, ApiResponse)
    @slot_blp.doc(
        security=[{"Bearer": []}],
        description="Create a new slot.",
        responses={
            201: "Slot created successfully.",
            400: "Bad Request",
            401: "Unauthorized",
            422: "Unprocessable Entity",
        },
    )
    @jwt_required(False)
    @parking_manager_role_required()
    def post(self, new_slot_data, user_id):
        print(new_slot_data)
        ParkingSlotService.create_slot(new_slot_data, user_id, request.remote_addr)
        return set_response(
            201, {"code": "success", "message": "Slot created successfully."}
        )


@slot_blp.route("/delete")
class DeleteSlot(MethodView):
    @slot_blp.arguments(DeleteSlotSchemaSchema)
    @slot_blp.response(200, ApiResponse)
    @slot_blp.doc(
        security=[{"Bearer": []}],
        description="Delete a slot.",
        responses={
            200: "Slot deleted successfully.",
            400: "Bad Request",
            401: "Unauthorized",
            422: "Unprocessable Entity",
        },
    )
    @parking_manager_role_required()
    @jwt_required(False)
    def delete(self, data, user_id):
        data.update({"ip_address": request.remote_addr, "manager_id": user_id})
        ParkingSlotService.delete_slot(data)
        return set_response(
            200, {"code": "success", "message": "Slot deleted successfully."}
        )


@slot_blp.route("/update")
class UpdateSlot(MethodView):
    @slot_blp.arguments(UpdateSlotSchemaSchema)
    @slot_blp.response(200, ApiResponse)
    @slot_blp.doc(
        security=[{"Bearer": []}],
        description="Update a slot.",
        responses={
            200: "Slot updated successfully.",
            400: "Bad Request",
            401: "Unauthorized",
        },
    )
    @parking_manager_role_required()
    @jwt_required(False)
    def post(self, slot_data, user_id):
        slot_data.update({"ip_address": request.remote_addr, "manager_id": user_id})
        ParkingSlotService.update_slot(slot_data)
        return set_response(
            200, {"code": "success", "message": "Slot updated successfully."}
        )

slot_blp.register_error_handler(
    NoSlotsFoundInTheGivenSlotCode, handle_no_slots_found_in_the_given_slot_code
)
slot_blp.register_error_handler(
    NoSlotsFoundInTheGivenEstablishment,handle_no_slots_found_in_the_given_establishment,
)
slot_blp.register_error_handler(
    NoSlotsFoundInTheGivenVehicleType, handle_no_slots_found_in_the_given_vehicle_type
)
slot_blp.register_error_handler(
    VehicleTypeDoesNotExist, handle_vehicle_type_does_not_exist
)
slot_blp.register_error_handler(SlotAlreadyExists, handle_slot_already_exists)
