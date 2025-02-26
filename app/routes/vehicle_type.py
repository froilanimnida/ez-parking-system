""" Routes for fetching vehicle types. """

# pylint: disable=missing-function-docstring

from flask import request
from flask.views import MethodView
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint

from app.routes.admin import admin_role_required
from app.schema.response_schema import ApiResponse
from app.schema.vehicle_type_schema import CreateVehicleTypeSchema
from app.services.vehicle_type_service import VehicleTypeService
from app.utils.response_util import set_response

vehicle_type_blp = Blueprint(
    "vehicle_type",
    __name__,
    url_prefix="/api/v1/vehicle-type",
    description="Vehicle Type API for EZ Parking System Frontend",
)


@vehicle_type_blp.route("/all")
class GetAllVehicleTypes(MethodView):
    """Get all vehicle types."""

    @vehicle_type_blp.response(200, ApiResponse)
    @vehicle_type_blp.doc(
        description="Get all vehicle types",
        responses={
            200: {"description": "Vehicle types retrieved successfully"},
            400: {"description": "Bad Request"},
        },
    )
    def get(self):
        vehicle_types = VehicleTypeService.get_all_vehicle_types()
        return set_response(
            200,
            {
                "code": "success",
                "message": "Vehicle Types Fetched",
                "vehicle_types": vehicle_types,
            },
        )


@vehicle_type_blp.route("/create")
class CreateVehicleType(MethodView):
    """Create a new vehicle type."""
    @vehicle_type_blp.arguments(CreateVehicleTypeSchema)
    @vehicle_type_blp.response(201, ApiResponse)
    @vehicle_type_blp.doc(
        security=[{"Bearer": []}],
        description="Create a new vehicle type.",
        responses={
            201: "Vehicle type created successfully.",
            400: "Bad Request",
            401: "Unauthorized",
        },
    )
    @jwt_required(False)
    @admin_role_required()
    def post(self, new_vehicle_type_data, admin_id):
        ip_address = request.remote_addr
        VehicleTypeService.create_new_vehicle_type(new_vehicle_type_data, admin_id, ip_address)
        return set_response(
            201,
            {
                "code": "success",
                "message": "Vehicle type created successfully.",
            },
        )

@vehicle_type_blp.route("/update")
class UpdateVehicleType(MethodView):
    """Update a vehicle type."""
    @vehicle_type_blp.response(200, ApiResponse)
    @vehicle_type_blp.doc(
        security=[{"Bearer": []}],
        description="Update a vehicle type.",
        responses={
            200: "Vehicle type updated successfully.",
            400: "Bad Request",
            401: "Unauthorized",
        },
    )
    @jwt_required(False)
    @admin_role_required()
    def patch(self):
        return set_response(
            200,
            {
                "code": "success",
                "message": "Vehicle type updated successfully.",
            },
        )
