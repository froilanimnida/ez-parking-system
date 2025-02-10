"""" Wraps the services that the parking manager can call """

from app.exceptions.slot_lookup_exceptions import SlotAlreadyExists
from app.models.audit_log import AuditLogRepository
from app.models.company_profile import CompanyProfileRepository
from app.models.parking_establishment import ParkingEstablishmentRepository
from app.models.parking_slot import ParkingSlotRepository
from app.utils.timezone_utils import get_current_time


class ParkingManagerService:  # pylint: disable=R0903
    """ Wraps all the services that the parking manager can call """
    @staticmethod
    def get_establishment_info(manager_id: int):
        """ Get parking establishment information """
        # return ParkingManagerOperations.get_establishment_info(manager_id)
    @staticmethod
    def get_all_slots(manager_id: int):
        """ Get all slots of the establishment """
        return SlotOperation.get_all_slots(manager_id)
    @staticmethod
    def create_slot(new_slot_data: dict, user_id: int, ip_address):
        """ Create a new slot """
        return SlotOperation.create_slot(user_id, new_slot_data, ip_address)


class SlotOperation:
    """ Wraps all the slot operations """
    @staticmethod
    def get_all_slots(manager_id: int):
        """ Get all slots of the establishment """
        profile_id = CompanyProfileRepository.get_company_profile(
            user_id=manager_id
        ).get("profile_id")
        establishment_id = ParkingEstablishmentRepository.get_establishment(
            profile_id=profile_id
        ).get("establishment_id")
        return ParkingSlotRepository.get_slots(establishment_id=establishment_id)
    @classmethod
    def create_slot(cls, manager_id, data, ip_address):
        """ Create a new slot """
        slot_exists = ParkingSlotRepository.get_slot(slot_code=data.get("slot_code"))
        if slot_exists:
            raise SlotAlreadyExists("Slot already exists.")
        now = get_current_time()
        profile_id = CompanyProfileRepository.get_company_profile(
            user_id=manager_id
        ).get("profile_id")
        establishment_id = ParkingEstablishmentRepository.get_establishment(
            profile_id=profile_id
        ).get("establishment_id")
        data.update({
            "establishment_id": establishment_id,
            "created_at": now,
            "updated_at": now,
        })
        ParkingSlotRepository.create_slot(data)
        return AuditLogRepository.create_audit_log({
            "action_type": "CREATE",
            "performed_by": manager_id,
            "details": f"Created new slot with slot code {data.get('slot_code')}",
            "performed_at": now,
            "ip_address": ip_address,
        })
