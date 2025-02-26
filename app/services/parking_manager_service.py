"""" Wraps the services that the parking manager can call """

from app.exceptions.slot_lookup_exceptions import SlotAlreadyExists
from app.models.address import AddressRepository
from app.models.audit_log import AuditLogRepository
from app.models.company_profile import CompanyProfileRepository
from app.models.parking_establishment import ParkingEstablishmentRepository
from app.models.parking_slot import ParkingSlotRepository
from app.models.user import UserRepository
from app.utils.timezone_utils import get_current_time


class ParkingManagerService:  # pylint: disable=R0903
    """ Wraps all the services that the parking manager can call """
    @staticmethod
    def get_all_slots(manager_id: int):
        """ Get all slots of the establishment """
        return SlotOperation.get_all_slots(manager_id)
    @staticmethod
    def create_slot(new_slot_data: dict, user_id: int, ip_address):
        """ Create a new slot """
        return SlotOperation.create_slot(user_id, new_slot_data, ip_address)
    @classmethod
    def get_company_profile(cls, user_id):
        """ Get company profile """
        return CompanyOperation.get_company_profile(user_id=user_id)

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


class CompanyOperation:
    """ Wraps all the company operations """
    @staticmethod
    def get_company_profile(user_id):
        """ Get company profile """
        user_info = UserRepository.get_user(user_id=user_id)
        company_profile = CompanyProfileRepository.get_company_profile(user_id=user_id)
        address_data = AddressRepository.get_address(profile_id=company_profile.get("profile_id"))
        parking_establishment = ParkingEstablishmentRepository.get_establishment(
            profile_id=company_profile.get("profile_id")
        )
        return {
            "user": user_info,
            "company_profile": company_profile,
            "address": address_data,
            "parking_establishment": parking_establishment
        }
    @staticmethod
    def update_company_profile(user_id: int, company_data: dict, address_data: dict):
        """ Update company profile """
        company_profile = CompanyProfileRepository.get_company_profile(user_id=user_id)
        CompanyProfileRepository.update_company_profile(
            profile_id=company_profile.get("profile_id"),
            company_data=company_data
        )
        AddressRepository.update_address(address_id=company_profile.get("profile_id"),
            address_data=address_data,
        )
        return {
            "company_profile": company_data,
            "address": address_data
        }

class ParkingEstablishmentService:  # pylint: disable=R0903
    """ Wraps all the parking establishment services """
    @staticmethod
    def get_establishment_info(manager_id: int):
        """ Get parking establishment information """
        profile_id = CompanyProfileRepository.get_company_profile(
            user_id=manager_id
        ).get("profile_id")
        establishment_data = ParkingEstablishmentRepository.get_establishment(
            profile_id=profile_id
        )
        address_data = AddressRepository.get_address(profile_id=profile_id)
        return {
            "establishment": establishment_data,
            "address": address_data
        }
