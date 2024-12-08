"""This module contains the business logic for vehicle type."""
from datetime import datetime

from app.models.audit_log import AuditLogRepository
from app.models.vehicle_type import VehicleRepository, VehicleTypeOperations


class VehicleTypeService:  # pylint: disable=R0903
    """Class for operations related to vehicle type."""

    @staticmethod
    def get_all_vehicle_types():
        """Get all vehicle types."""
        return GetVehicleType.get_all_vehicle_types()
    @classmethod
    def create_new_vehicle_type(cls, new_vehicle_type_data, admin_id):
        """Create a new vehicle type."""
        return CreateNewVehicleType.create_new_vehicle_type(new_vehicle_type_data, admin_id)


class GetVehicleType:  # pylint: disable=R0903
    """Wraps the logic for getting the list of vehicle types, calling the model layer classes."""

    @staticmethod
    def get_all_vehicle_types():
        """Get all vehicle types."""
        return VehicleRepository.get_all_vehicle_types()


class CreateNewVehicleType:  # pylint: disable=R0903
    """Class for operations related to creating vehicle type."""

    @staticmethod
    def create_new_vehicle_type(new_vehicle_type_data, admin_id):
        """Create a new vehicle type."""
        VehicleTypeOperations.create_new_vehicle_type(new_vehicle_type_data)
        return AuditLogRepository.create_audit_log({
            "admin_id": admin_id,
            "table_name": "vehicle_type",
            "action_type": "CREATE",
            "details": "Vehicle Type Created",
            "timestamp": datetime.now(),
        })
