"""Wraps the error handlers for the vehicle type related errors."""

from app.exceptions.vehicle_type_exceptions import VehicleTypeDoesNotExist
from app.utils.error_handlers.base_error_handler import handle_error


def handle_vehicle_type_does_not_exist(error):
    """This function handles vehicle type doesn't exist errors."""
    if isinstance(error, VehicleTypeDoesNotExist):
        return handle_error(
            error,
            404,
            "vehicle_type_does_not_exist",
            "Vehicle type doesn't exist.",
        )
    raise error
