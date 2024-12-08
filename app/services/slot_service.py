""" This module contains the logic for getting the list of slots. """

from datetime import datetime

from app.exceptions.slot_lookup_exceptions import (
    NoSlotsFoundInTheGivenSlotCode,
)
from app.models.audit_log import AuditLogRepository
from app.models.company_profile import CompanyProfileRepository
from app.models.parking_establishment import ParkingEstablishmentRepository
from app.models.parking_slot import ParkingSlotRepository


class ParkingSlotService:
    """Wraps the logic for getting the list of slots."""

    @staticmethod
    def get_all_slots(establishment_uuid: bytes):  # pylint: disable=C0116
        return GetSlotService.get_all_slots(establishment_uuid)

    @staticmethod
    def get_slots_by_vehicle_type(
        vehicle_type_id: int, establishment_id: int
    ):  # pylint: disable=C0116
        return GetSlotService.get_slots_by_vehicle_type(
            vehicle_type_id, establishment_id
        )

    @staticmethod
    def get_slot(slot_uuid: bytes):  # pylint: disable=C0116
        return GetSlotService.get_slot(slot_uuid)
    
    @staticmethod
    def create_slot(new_slot_data: dict, user_id: int, ip_address):  # pylint: disable=C0116
        return AddingSlotService.create_slot(new_slot_data, user_id, ip_address)
    
    @staticmethod
    def delete_slot(slot_data: dict):
        """Delete a slot."""
        return DeleteSlotService.delete_slot(slot_data)
    
    @staticmethod
    def update_slot(slot_data: dict, user_id: int, ip_address):
        """Update a slot."""
        return UpdateSlotService.update_slot(slot_data, slot_data, ip_address)


class GetSlotService:
    """Wraps the logic for getting the list of slots, calling the model layer classes."""
    @staticmethod
    def get_all_slots(establishment_uuid: bytes):  # pylint: disable=C0116
        return ParkingSlotRepository.get_slots(
            establishment_id=ParkingEstablishmentRepository.get_establishment(
            establishment_uuid
        ).get("establishment_id"))
    
    @staticmethod
    def get_slots_by_vehicle_type(vehicle_type_id: int, establishment_uuid: bytes):
        return ParkingSlotRepository.get_slots_by_criteria({
            "vehicle_type_id": vehicle_type_id,
            "establishment_id": ParkingEstablishmentRepository.get_establishment(
                establishment_uuid
            ).get("establishment_id")
        })
        
    @staticmethod
    def get_slot(slot_uuid: bytes):
        """Get slot by slot code."""
        slot = ParkingSlotRepository.get_slot(slot_uuid)
        if slot is None:
            raise NoSlotsFoundInTheGivenSlotCode(
                "No slots found.."
            )
        return {"slot_info": slot}


class AddingSlotService:  # pylint: disable=R0903
    """Wraps the logic for creating a new slot."""
    @staticmethod
    def create_slot(new_slot_data: dict, user_id: int, ip_address):  # pylint: disable=C0116
        company_profile_id = CompanyProfileRepository.get_company_profile_by_user_id(user_id).get("profile_id")
        new_slot_data.update({
            "establishment_id": ParkingEstablishmentRepository.get_establishment(
                profile_id=company_profile_id
            ).get("establishment_id"),
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        })
        ParkingSlotRepository.create_slot(new_slot_data)
        AuditLogRepository.create_audit_log({
            "action_type": "CREATE",
            "performed_by": user_id,
            "details": f"Created new slot with slot code {new_slot_data.get('slot_code')}",
            "performed_at": datetime.now(),
            "ip_address": ip_address,
        })
        
class DeleteSlotService:  # pylint: disable=R0903
    @staticmethod
    def delete_slot(slot_data):
        """Delete a slot."""
        user_id = slot_data.get("user_id")
        slot_uuid = slot_data.get("slot_uuid")
        return ParkingSlotRepository.delete_slot(slot_data)


class UpdateSlotService:  # pylint: disable=R0903
    @staticmethod
    def update_slot(slot_data, user_id, ip_address):
        """Update a slot."""
        slot_id = ParkingSlotRepository.update_slot(slot_data)
        return AuditLogRepository.create_audit_log({
            "action_type": "UPDATE",
            "performed_by": user_id,
            "details": f"Updated slot with slot code {slot_id}",
            "performed_at": datetime.now(),
            "ip_address": ip_address,
        })