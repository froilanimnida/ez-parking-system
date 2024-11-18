""" Wraps all function of role parking manager. """

# pylint: disable=missing-function-docstring, missing-class-docstring

from functools import wraps

from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt
from flask_smorest import Blueprint

from app.exceptions.slot_lookup_exceptions import SlotNotFound
from app.schema.parking_manager_validation import (
    CreateSlotSchema,
    EstablishmentIdValidationSchema,
    EstablishmentValidationSchema,
    UpdateEstablishmentInfoSchema,
    UpdateSlotSchema,
)
from app.schema.response_schema import ApiResponse
from app.services.establishment_service import EstablishmentService
from app.services.slot_service import SlotService
from app.utils.error_handlers.slot_lookup_error_handlers import handle_slot_not_found
from app.utils.response_util import set_response

parking_manager_blp = Blueprint(
    "parking_manager",
    __name__,
    url_prefix="/api/v1/parking-manager",
    description="Parking Manager API for EZ Parking System Frontend",
)


def parking_manager_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            is_parking_manager = (
                get_jwt().get("sub", {}).get("role") == "parking_manager"
            )
            if not is_parking_manager:
                return set_response(
                    401,
                    {"code": "unauthorized", "message": "Parking manager required."},
                )
            return fn(*args, **kwargs)

        return decorator

    return wrapper


@parking_manager_blp.route("/establishment/create")
class CreateEstablishment(MethodView):
    @parking_manager_blp.arguments(EstablishmentValidationSchema)
    @parking_manager_blp.response(201, ApiResponse)
    @parking_manager_blp.doc(
        security=[{"Bearer": []}],
        description="Create a new parking establishment.",
        responses={
            201: "Establishment created successfully.",
            400: "Bad Request",
            401: "Unauthorized",
        },
    )
    @jwt_required(True)
    @parking_manager_required()
    def post(self, new_establishment_data):
        new_establishment_data["manager_id"] = get_jwt().get("sub", {}).get("user_id")
        if get_jwt().get("sub", {}).get("role") != "parking_manager":
            return set_response(
                403,
                {
                    "code": "forbidden",
                    "message": "Only parking managers can create establishments.",
                },
            )
        EstablishmentService.create_new_parking_establishment(new_establishment_data)
        return set_response(
            201,
            {
                "code": "success",
                "message": "Parking establishment created successfully.",
            },
        )


@parking_manager_blp.route("/establishment/delete")
class DeleteEstablishment(MethodView):
    @parking_manager_blp.arguments(EstablishmentIdValidationSchema)
    @parking_manager_blp.response(200, ApiResponse)
    @parking_manager_blp.doc(
        security=[{"Bearer": []}],
        description="Delete parking establishment.",
        responses={
            200: "Parking establishment deleted successfully.",
            400: "Bad Request",
            401: "Unauthorized",
        },
    )
    @jwt_required(False)
    @parking_manager_required()
    def delete(self, request):
        establishment_id = request.get("establishment_id")
        EstablishmentService.delete_establishment(establishment_id)
        return set_response(
            200,
            {
                "code": "success",
                "message": "Parking establishment deleted successfully.",
            },
        )


@parking_manager_blp.route("/establishment/update")
class UpdateEstablishment(MethodView):
    @parking_manager_blp.arguments(UpdateEstablishmentInfoSchema)
    @parking_manager_blp.response(200, ApiResponse)
    @parking_manager_blp.doc(
        security=[{"Bearer": []}],
        description="Update parking establishment information.",
        responses={
            200: "Establishment updated successfully.",
            400: "Bad Request",
            401: "Unauthorized",
        },
    )
    @jwt_required(False)
    @parking_manager_required()
    def patch(self, establishment_data):
        current_user = get_jwt()
        if current_user.get("role") not in ["parking_manager", "admin"]:
            return {"code": "error", "message": "Unauthorized"}, 401

        establishment_id = establishment_data.pop("establishment_id", None)
        EstablishmentService.update_establishment(
            establishment_id=establishment_id, establishment_data=establishment_data
        )

        return set_response(
            200,
            {
                "code": "success",
                "message": "Establishment updated successfully.",
            },
        )


@parking_manager_blp.route("/slot/create")
class CreateSlot(MethodView):
    @parking_manager_blp.arguments(CreateSlotSchema)
    @parking_manager_blp.response(201, ApiResponse)
    @parking_manager_blp.doc(
        security=[{"Bearer": []}],
        description="Create a new slot.",
        responses={
            201: "Slot created successfully.",
            400: "Bad Request",
            401: "Unauthorized",
        },
    )
    @parking_manager_required()
    @jwt_required(False)
    def post(self, new_slot_data):
        new_slot_data["manager_id"] = get_jwt().get("sub", {}).get("user_id")
        SlotService.create_slot(new_slot_data)
        return set_response(201, "Slot created successfully.")


@parking_manager_blp.route("/slot/delete")
class DeleteSlot(MethodView):
    @parking_manager_blp.arguments(EstablishmentIdValidationSchema)
    @parking_manager_blp.response(200, ApiResponse)
    @parking_manager_blp.doc(
        security=[{"Bearer": []}],
        description="Delete a slot.",
        responses={
            200: "Slot deleted successfully.",
            400: "Bad Request",
            401: "Unauthorized",
        },
    )
    @parking_manager_required()
    @jwt_required(False)
    def delete(self, request):
        data = request.get_json()
        manager_id = get_jwt().get("sub", {}).get("user_id")
        print(data, manager_id)
        return set_response(200, "Slot deleted successfully.")


@parking_manager_blp.route("/slot/update", methods=["POST"])
class UpdateSlot(MethodView):

    @parking_manager_blp.arguments(UpdateSlotSchema)
    @parking_manager_blp.response(200, ApiResponse)
    @parking_manager_blp.doc(
        security=[{"Bearer": []}],
        description="Update a slot.",
        responses={
            200: "Slot updated successfully.",
            400: "Bad Request",
            401: "Unauthorized",
        },
    )
    @parking_manager_required()
    @jwt_required(False)
    def post(self, request):
        manager_id = get_jwt().get("sub", {}).get("user_id")
        print(manager_id, request)
        return set_response(200, "Slot updated successfully.")


parking_manager_blp.register_error_handler(SlotNotFound, handle_slot_not_found)
