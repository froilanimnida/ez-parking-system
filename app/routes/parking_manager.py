""" Wraps all function of role parking manager. """

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt

from app.exceptions.slot_lookup_exceptions import SlotNotFound
from app.schema.slot_validation import SlotValidationSchema
from app.services.slot_service import SlotService
from app.utils.error_handlers.slot_lookup_error_handlers import handle_slot_not_found
from app.utils.response_util import set_response

parking_manager_bp = Blueprint("parking_manager", __name__)

parking_manager_bp.register_error_handler(SlotNotFound, handle_slot_not_found)


@parking_manager_bp.route("/v1/parking-manager/slot/create", methods=["POST"])
@jwt_required(optional=False)
def create_slot():
    """Create a new slot."""
    data = request.get_json()
    data["manager_id"] = get_jwt().get("sub").get("user_id")  # type: ignore
    slot_validation_schema = SlotValidationSchema()
    new_slot_data = slot_validation_schema.load(data)
    SlotService.create_slot(new_slot_data)  # type: ignore
    return set_response(201, "Slot created successfully.")


@parking_manager_bp.route("/v1/parking-manager/slot/delete", methods=["POST"])
@jwt_required(optional=False)
def delete_slot():
    """Delete a slot."""
    data = request.get_json()
    get_jwt().get("sub").get("user_id")  # type: ignore
    print(data)
    return set_response(200, "Slot deleted successfully.")


@parking_manager_bp.route("/v1/parking-manager/slot/update", methods=["POST"])
@jwt_required(optional=False)
def update_slot():
    """Update a slot."""
    data = request.get_json()
    get_jwt().get("sub").get("user_id")  # type: ignore
    print(data)
    return set_response(200, "Slot updated successfully.")
