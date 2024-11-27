"""This module contains the business logic for vehicle type."""

from app.models.vehicle_type import VehicleTypeOperations


class VehicleTypeService:  # pylint: disable=R0903
    """Class for operations related to vehicle type."""

    @staticmethod
    def get_all_vehicle_types():
        """Get all vehicle types."""
        return GetVehicleType.get_all_vehicle_types()


class GetVehicleType:  # pylint: disable=R0903
    """Wraps the logic for getting the list of vehicle types, calling the model layer classes."""

    @staticmethod
    def get_all_vehicle_types():
        """Get all vehicle types."""
        return VehicleTypeOperations.get_all_vehicle_types()
