""" This module contains the logic for getting the list of slots. """

# pylint: disable=missing-function-docstring, too-few-public-methods

from datetime import datetime

from app.exceptions.slot_lookup_exceptions import NoSlotsFoundInTheGivenSlotCode, SlotAlreadyExists
from app.models.audit_log import AuditLogRepository
from app.models.parking_establishment import ParkingEstablishmentRepository, ParkingEstablishment
from app.models.parking_slot import ParkingSlotRepository


class ParkingSlotService:
    """Wraps the logic for getting the list of slots."""
    @staticmethod
    def get_all_slots(establishment_uuid: bytes):
        return GetSlotService.get_all_slots(establishment_uuid)
    @staticmethod
    def get_slots_by_vehicle_type(vehicle_type_id: int, establishment_id: int):
        return GetSlotService.get_slots_by_vehicle_type(vehicle_type_id, establishment_id)
    @staticmethod
    def get_slot(slot_uuid: bytes):
        return GetSlotService.get_slot(slot_uuid)
    @staticmethod
    def create_slot(new_slot_data: dict, user_id: int, ip_address):
        return AddSlotService.create_slot(new_slot_data, user_id, ip_address)
    @staticmethod
    def delete_slot(slot_data: dict):
        """Delete a slot."""
        return DeleteSlotService.delete_slot(slot_data)
    @staticmethod
    def update_slot(slot_data: dict):
        """Update a slot."""
        return UpdateSlotService.update_slot(slot_data)

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


class AddSlotService:
    """Wraps the logic for creating a new slot."""
    @staticmethod
    def create_slot(new_slot_data: dict, user_id: int, ip_address):  # pylint: disable=C0116
        slot_exists = ParkingSlotRepository.get_slot(new_slot_data.get("slot_code"))
        if slot_exists:
            raise SlotAlreadyExists("Slot already exists.")
        now = datetime.now()
        establishment_id = ParkingEstablishment.get_establishment_id(
            new_slot_data.pop("establishment_uuid")
        )
        new_slot_data.update({
            "establishment_id": establishment_id,
            "created_at": now,
            "updated_at": now,
        })
        ParkingSlotRepository.create_slot(new_slot_data)
        return AuditLogRepository.create_audit_log({
            "action_type": "CREATE",
            "performed_by": user_id,
            "details": f"Created new slot with slot code {new_slot_data.get('slot_code')}",
            "performed_at": now,
            "ip_address": ip_address,
        })
class DeleteSlotService:
    """Wraps the logic for deleting a slot."""
    @staticmethod
    def delete_slot(slot_data):
        """Delete a slot."""
        slot_id = ParkingSlotRepository.delete_slot(slot_data.get("slot_uuid"))
        AuditLogRepository.create_audit_log({
            "action_type": "DELETE",
            "performed_by": slot_data.get("user_id"),
            "details": f"Deleted slot with slot id: {slot_id}",
            "performed_at": datetime.now(),
            "ip_address": slot_data.get("ip_address"),
        })

class UpdateSlotService:  # pylint: disable=R0903
    """Update a slot."""
    @staticmethod
    def update_slot(slot_data):
        slot_id = ParkingSlotRepository.update_slot(slot_data)
        return AuditLogRepository.create_audit_log({
            "action_type": "UPDATE",
            "performed_by": slot_data.get("user_id"),
            "details": f"Updated slot with slot code {slot_id}",
            "performed_at": datetime.now(),
            "ip_address": slot_data.get("ip_address"),
        })
