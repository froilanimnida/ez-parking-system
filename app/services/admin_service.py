""" Wraps the operations that can be performed by the admin. """

# pylint: disable=C0301, C0116

from flask import render_template

from app.models.audit_log import AuditLogRepository
from app.models.ban_user import BanUserRepository
from app.models.company_profile import CompanyProfileRepository
from app.models.parking_establishment import ParkingEstablishmentRepository
from app.models.user import UserRepository
from app.tasks import send_mail
from app.utils.timezone_utils import get_current_time

class AdminService:
    """Service class for admin operations."""
    @staticmethod
    def get_user(user_id: int) -> dict:
        """Get user information."""
        return UserManagementService.get_user(user_id)

    @staticmethod
    def ban_user(ban_data: dict, admin_id, ip_address) -> int:
        return UserBanningService.ban_user(ban_data, admin_id, ip_address)

    @staticmethod
    def unban_user(ban_id: int) -> int:
        return UserBanningService.unban_user(ban_id)
    @staticmethod
    def get_establishments() -> list:
        """Get all parking applicants."""
        return ParkingManagerOperations.get_establishments()
    @staticmethod
    def approve_parking_applicant(establishment_uuid: bytes) -> None:
        """Approve a parking applicant."""
        return ParkingManagerOperations.approve_parking_applicant(establishment_uuid)
    @staticmethod
    def get_all_users() -> list[dict]:
        """Get all users."""
        return UserManagementService.get_users()



class UserBanningService:
    """Service class for banning plate numbers."""
    @staticmethod
    def ban_user(ban_data: dict, admin_id, ip_address) -> int:
        """Ban a user."""
        user = UserRepository.get_user(user_uuid=ban_data.pop('uuid'))
        ban_data.update({"user_id": user.get("user_id")})
        BanUserRepository.ban_user(ban_data)
        ban_template = render_template(
            '/ban.html', reason=ban_data.get("reason"), email=user.get('email')
        )
        send_mail(user.get("email"), ban_template, 'You have been banned')
        return AuditLogRepository.create_audit_log({
            "action_type": "CREATE",
            "performed_by": admin_id,
            "target_user": user.get("user_id"),
            "details": f"User with user_id {ban_data['user_id']} has been banned.",
            "performed_at": get_current_time(),
            "ip_address": ip_address
        })

    @staticmethod
    def unban_user(ban_id: int): # pylint: disable=unused-argument
        """Unban a user."""
        BanUserRepository.unban_user(ban_id)


class ParkingManagerOperations:
    """Service class for parking applicant operations."""
    @staticmethod
    def get_establishments() -> list:
        """Get all parking establishments (both verified and non-verified)."""
        establishments = []
        non_verified_parking_establishments = ParkingEstablishmentRepository.get_establishments(
            verification_status=False)
        verified_parking_establishments = ParkingEstablishmentRepository.get_establishments(
            verification_status=True
        )
        all_parking_establishments = non_verified_parking_establishments + verified_parking_establishments
        if not all_parking_establishments:
            return []
        company_profile_ids = list({est['profile_id'] for est in all_parking_establishments})
        company_profiles = CompanyProfileRepository.get_company_profiles(
            profile_ids=company_profile_ids
        )
        profile_map = {profile['profile_id']: profile for profile in company_profiles}
        for establishment in all_parking_establishments:
            profile = profile_map.get(establishment['profile_id'])
            if profile:
                establishments.append({
                    "establishment": establishment,
                    "company_profile": profile
                })
        return establishments
    @staticmethod
    def approve_parking_applicant(establishment_uuid: bytes) -> None:
        """Approve a parking applicant."""
        ParkingEstablishmentRepository.verify_parking_establishment(
            establishment_uuid=establishment_uuid
        )

class UserManagementService:  # pylint: disable=too-few-public-methods
    """Service class for user management operations."""
    @staticmethod
    def get_user(user_id: int) -> dict:
        """Get user information."""
        return UserRepository.get_user(user_id=user_id)
    @staticmethod
    def get_users() -> list[dict]:
        """Get all users."""
        users = UserRepository.get_all_users()
        for user in users:
            ban_id = BanUserRepository.get_ban_id(user['user_id'])
            if ban_id:
                user['ban_id'] = ban_id
        return users
