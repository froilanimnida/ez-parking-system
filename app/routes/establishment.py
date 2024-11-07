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
from app.utils.error_handlers import (
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
    if not data:
        return set_response(400, {"code": "error", "message": "Invalid request data."})
    new_establishment_data = establishment_schema.load(data)
    EstablishmentService.create_new_parking_establishment(
        new_establishment_data  # type: ignore
    )
    return set_response(
        201,
        {"code": "success", "message": "Parking establishment created successfully."},
    )


@establishment.route("/v1/establishment/get-all", methods=["GET"])
def get_all_establishments():
    """Get all parking establishments."""
    establishments = EstablishmentService.get_all_establishments()
    return set_response(
        200,
        {
            "code": "success",
            "message": "Parking establishments retrieved successfully.",
            "establishments": establishments,
        },
    )


@establishment.route("/v1/establishment/get-nearest", methods=["GET"])
def get_nearest_establishments():
    """Get nearest parking establishments based on the current user location."""
    data = request.json
    if not data:
        return set_response(
            400,
            {
                "code": "long_lat_missing",
                "message": "You need to provide latitude and longitude.",
            },
        )
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    if not latitude or not longitude:
        return set_response(
            400, {"code": "error", "message": "Please provide latitude and longitude."}
        )
    establishments = EstablishmentService.get_nearest_establishments(
        latitude, longitude
    )
    return set_response(
        200,
        {
            "code": "success",
            "message": "Nearest parking establishments retrieved successfully.",
            "establishments": establishments,
        },
    )


@establishment.route("/v1/establishment/get-24-hours", methods=["GET"])
def get_24_hours_establishments():
    """Get parking establishments that are open 24 hours."""
    establishments = EstablishmentService.get_24_hours_establishments()
    return set_response(
        200,
        {
            "code": "success",
            "message": "24 hours parking establishments retrieved successfully.",
            "establishments": establishments,
        },
    )


@establishment.route("/v1/establishment/update-establishment", methods=["PATCH"])
@jwt_required(optional=True)
def update_establishment():
    """Update parking establishment data."""
    data = request.json
    current_user = get_jwt()
    if current_user.get("role") not in ['parking_manager', 'admin']:
        return set_response(
            401,
            {
                "code": "error",
                "message": "You are not authorized to perform this action.",
            },
        )
    data["manager_id"] = current_user.get("sub").get("user_id")  # type: ignore
    establishment_schema = UpdateEstablishmentInfoSchema()
    if not data:
        return set_response(400, {"code": "error", "message": "Invalid request data."})
    establishment_id = data["establishment_id"]
    updated_establishment_data = establishment_schema.load(data)
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
