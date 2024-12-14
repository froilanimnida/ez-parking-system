""" Wraps the operations that can be performed by the admin. """

from datetime import datetime

from app.models.address import AddressRepository
from app.models.audit_log import AuditLogRepository
from app.models.ban_user import BanUserRepository
from app.models.company_profile import CompanyProfileRepository
from app.models.establishment_document import EstablishmentDocumentRepository
from app.models.operating_hour import OperatingHoursRepository
from app.models.parking_establishment import ParkingEstablishmentRepository
from app.models.parking_slot import ParkingSlotRepository
from app.models.payment_method import PaymentMethodRepository
from app.models.pricing_plan import PricingPlanRepository
from app.models.user import UserRepository
from app.utils.bucket import R2TransactionalUpload


# pylint: disable=C0116


class AdminService:
    """Service class for admin operations."""

    @staticmethod
    def ban_user(ban_data: dict, admin_id) -> int:
        return UserBanningService.ban_user(ban_data, admin_id)

    @staticmethod
    def unban_user(user_id: int, admin_id: int, ip_address: str) -> int:
        return UserBanningService.unban_user(user_id, admin_id, ip_address)
    @staticmethod
    def get_parking_applicants() -> list:
        """Get all parking applicants."""
        return ParkingApplicantService.get_parking_applicants()
    @staticmethod
    def get_parking_details(parking_establishment_uuid: bytes) -> dict:
        """Get parking establishment applicant details."""
        return ParkingApplicantService.get_parking_details(parking_establishment_uuid)
    @staticmethod
    def approve_parking_applicant(establishment_uuid: bytes) -> None:
        """Approve a parking applicant."""
        return ParkingApplicantService.approve_parking_applicant(establishment_uuid)



class UserBanningService:
    """Service class for banning plate numbers."""

    @staticmethod
    def ban_user(ban_data: dict, admin_id) -> int:
        """Ban a user."""
        BanUserRepository.ban_user(ban_data)
        return AuditLogRepository.create_audit_log({
            "action_type": "CREATE",
            "performed_by": admin_id,
            "target_user": ban_data['user_id'],
            "details": f"User with user_id {ban_data['user_id']} has been banned.",
            "performed_at": datetime.now(),
            "ip_address": ban_data['ip_address']
        })

    @staticmethod
    def unban_user(user_id: int, admin_id: int, ip_address: str) -> int:
        """Unban a user."""
        BanUserRepository.unban_user(user_id)
        return AuditLogRepository.create_audit_log({
            "action_type": "DELETE",
            "performed_by": admin_id,
            "target_user": user_id,
            "details": f"User with user_id {user_id} has been unbanned.",
            "performed_at": datetime.now(),
            "ip_address": ip_address
        })


class ParkingApplicantService:
    """Service class for parking applicant operations."""
    @staticmethod
    def get_parking_applicants() -> list:
        """Get all parking applicants."""
        applicants = []
        non_verified_parking_establishments = ParkingEstablishmentRepository.get_establishments(
            verification_status=False
        )
        if len(non_verified_parking_establishments) == 0:
            return []
        company_profile_ids = [
            parking_establishment['profile_id']
            for parking_establishment in non_verified_parking_establishments
        ]
        non_verified_company_profiles = CompanyProfileRepository.get_company_profiles(
            profile_ids=company_profile_ids
        )
        for establishment in non_verified_parking_establishments:
            profile = next((
                profile for profile in non_verified_company_profiles
                if profile.profile_id == establishment[
                'profile_id'
            ]
            ), None)
            if profile:
                applicant = {
                    "establishment": establishment,
                    "company_profile": profile.to_dict()
                }
                applicants.append(applicant)
        return applicants
    @staticmethod
    def get_parking_details(parking_establishment_uuid: bytes) -> dict:
        """Get parking establishment applicant details."""
        parking_establishment_details = ParkingEstablishmentRepository.get_establishment(
            establishment_uuid=parking_establishment_uuid
        )
        parking_establishment_id = parking_establishment_details['establishment_id']
        parking_establishment_operating_hours = OperatingHoursRepository.get_operating_hours(
            establishment_id=parking_establishment_id
        )
        parking_establishment_slot = ParkingSlotRepository.get_slots(
            establishment_id=parking_establishment_id
        )
        parking_establishment_payment_methods = PaymentMethodRepository.get_payment_methods(
            establishment_id=parking_establishment_id
        )
        parking_establishment_pricing_plans = PricingPlanRepository.get_pricing_plans(
            establishment_id=parking_establishment_id
        )
        company_details = CompanyProfileRepository.get_company_profile(
            profile_id=parking_establishment_details['profile_id']
        )
        parking_establishment_documents = (EstablishmentDocumentRepository
        .get_establishment_documents(
            establishment_id=parking_establishment_id
        ))
        parking_establishment_address = AddressRepository.get_address(
            profile_id=company_details.profile_id
        )
        user_details = UserRepository.get_user(user_id=company_details.user_id)
        r2_instance = R2TransactionalUpload()
        parking_establishment_documents_object = [
            {
                **document,
                "url": r2_instance.download(document['bucket_path'])
            } for document in parking_establishment_documents
        ]
        return {
            "establishment": parking_establishment_details,
            "operating_hours": parking_establishment_operating_hours,
            "slots": parking_establishment_slot,
            "payment_methods": parking_establishment_payment_methods,
            "pricing_plans": parking_establishment_pricing_plans,
            "company_profile": company_details,
            "documents": parking_establishment_documents,
            "address": parking_establishment_address,
            "user": user_details,
            "documents_object": parking_establishment_documents_object
        }
    @staticmethod
    def approve_parking_applicant(establishment_uuid: bytes) -> None:
        """Approve a parking applicant."""
        return ParkingEstablishmentRepository.verify_parking_establishment(
            establishment_uuid=establishment_uuid
        )
