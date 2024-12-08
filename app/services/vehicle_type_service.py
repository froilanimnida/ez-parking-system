"""This module contains the business logic for vehicle type."""
from datetime import datetime

from app.models.audit_log import AuditLogRepository
from app.models.vehicle_type import VehicleRepository


class VehicleTypeService:  # pylint: disable=R0903
    """Class for operations related to vehicle type."""

    @staticmethod
    def get_all_vehicle_types():
        """Get all vehicle types."""
        return GetVehicleType.get_all_vehicle_types()
    @classmethod
    def create_new_vehicle_type(cls, new_vehicle_type_data, admin_id, ip_address):
        """Create a new vehicle type."""
        return CreateNewVehicleType.create_new_vehicle_type(
            new_vehicle_type_data, admin_id, ip_address
        )
    
    @classmethod
    def update_vehicle_type(cls, vehicle_type_data, admin_id, ip_address):
        """Update vehicle type."""
        return UpdateVehicleType.update_vehicle_type(
            vehicle_type_data, admin_id, ip_address
        )


class GetVehicleType:  # pylint: disable=R0903
    """Wraps the logic for getting the list of vehicle types, calling the model layer classes."""

    @staticmethod
    def get_all_vehicle_types():
        """Get all vehicle types."""
        return VehicleRepository.get_all_vehicle_types()


class CreateNewVehicleType:  # pylint: disable=R0903
    """Class for operations related to creating vehicle type."""

    @staticmethod
    def create_new_vehicle_type(new_vehicle_type_data, admin_id, ip_address):
        """Create a new vehicle type."""
        new_vehicle_type_id = VehicleRepository.create_vehicle_type(new_vehicle_type_data)
        return AuditLogRepository.create_audit_log({
            "action_type": "CREATE",
            "performed_by": admin_id,
            "details": f"Vehicle Type Created with ID: {new_vehicle_type_id}",
            "performed_at": datetime.now(),
            "ip_address": ip_address
        })


class UpdateVehicleType:  # pylint: disable=R0903
    @staticmethod
    def update_vehicle_type(vehicle_type_data, user_id, ip_address):
        """Update vehicle type."""
        vehicle_type_id = VehicleRepository.update_vehicle_type(vehicle_type_data)
        return AuditLogRepository.create_audit_log({
            "action_type": "UPDATE",
            "performed_by": user_id,
            "details": f"Vehicle Type Updated with ID: {vehicle_type_id}",
            "performed_at": datetime.now(),
            "ip_address": ip_address
        })