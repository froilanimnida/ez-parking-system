""" Routes for fetching vehicle types. """

# pylint: disable=missing-function-docstring

from flask.views import MethodView
from flask_smorest import Blueprint

from app.schema.response_schema import ApiResponse
from app.services.vehicle_type_service import VehicleTypeService
from app.utils.response_util import set_response


vehicle_type_blp = Blueprint(
    "vehicle_type",
    __name__,
    url_prefix="/api/v1/vehicle-type",
    description="Vehicle Type API for EZ Parking System Frontend",
)


@vehicle_type_blp.route("/get-all-vehicle-types")
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
