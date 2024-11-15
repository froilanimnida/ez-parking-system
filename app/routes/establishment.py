""" Routes related to parking establishment. """

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt

from app.exceptions.establishment_lookup_exceptions import (
    EstablishmentDoesNotExist,
    EstablishmentEditsNotAllowedException,
)
from app.schema.establishment_validation import (
    EstablishmentValidationSchema,
    UpdateEstablishmentInfoSchema,
)
from app.services.establishment_service import EstablishmentService
from app.utils.error_handlers.establishment_error_handlers import (
    handle_establishment_does_not_exist,
    handle_establishment_edits_not_allowed,
)
from app.utils.response_util import set_response

establishment = Blueprint("establishment", __name__)

establishment.register_error_handler(
    EstablishmentDoesNotExist, handle_establishment_does_not_exist
)
establishment.register_error_handler(
    EstablishmentEditsNotAllowedException, handle_establishment_edits_not_allowed
)


@establishment.route("/v1/establishment/create", methods=["POST"])
@jwt_required(optional=True)
def create_establishment():
    """Create a new parking establishment."""
    current_user = get_jwt()
    data = request.json
    data["manager_id"] = current_user.get("sub").get("user_id")  # type: ignore
    if current_user.get("role") != "parking_manager":
        return set_response(
            403,
            {
                "code": "forbidden",
                "message": "Only parking managers can create establishments.",
            },
        )
    establishment_schema = EstablishmentValidationSchema()
    new_establishment_data = establishment_schema.load(data)  # type: ignore
    EstablishmentService.create_new_parking_establishment(
        new_establishment_data  # type: ignore
    )
    return set_response(
        201,
        {"code": "success", "message": "Parking establishment created successfully."},
    )


@establishment.route("/v1/user/query/establishments", methods=["GET"])
def get_establishments():
    """Get establishments with optional filters and sorting"""
    args = request.args

    latitude = args.get("latitude", type=float, default=None)
    longitude = args.get("longitude", type=float, default=None)

    is_24_hours = args.get("is_24_hours", type=bool, default=True)
    vehicle_type_id = args.get("vehicle_type_id", type=int, default=None)
    establishment_name = args.get("establishment_name", type=str, default=None)
    query_params = {
        "latitude": latitude,
        "longitude": longitude,
        "is_24_hours": is_24_hours,
        "vehicle_type_id": vehicle_type_id,
        "establishment_name": establishment_name,
    }

    establishments = EstablishmentService.get_establishments(query_params)

    return set_response(
        200,
        {
            "code": "success",
            "message": "Establishments retrieved successfully.",
            "establishments": establishments,
        },
    )


@establishment.route("/v1/establishment/update-establishment", methods=["PATCH"])
@jwt_required(optional=True)
def update_establishment():
    """Update parking establishment data."""
    data = request.json
    current_user = get_jwt()
    if current_user.get("role") not in ["parking_manager", "admin"]:
        return set_response(
            401,
            {
                "code": "error",
                "message": "You are not authorized to perform this action.",
            },
        )
    data["manager_id"] = current_user.get("sub").get("user_id")  # type: ignore
    establishment_schema = UpdateEstablishmentInfoSchema()
    establishment_id = data["establishment_id"]  # type: ignore
    updated_establishment_data = establishment_schema.load(data)  # type: ignore
    EstablishmentService.update_establishment(
        establishment_id=establishment_id,
        establishment_data=updated_establishment_data,  # type: ignore
    )
    return set_response(
        200,
        {"code": "success", "message": "Parking establishment updated successfully."},
    )


@establishment.route("/v1/establishment/delete-establishment", methods=["DELETE"])
@jwt_required(optional=False)
def delete_establishment():
    """Delete a parking establishment."""
    data = request.json
    if not data:
        return set_response(400, {"code": "error", "message": "Invalid request data."})
    establishment_id = data.get("establishment_id")
    EstablishmentService.delete_establishment(establishment_id)
    return set_response(
        200,
        {"code": "success", "message": "Parking establishment deleted successfully."},
    )
