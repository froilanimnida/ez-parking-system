""" Wraps the operations that can be performed by the admin. """

from datetime import datetime

import pytz
from flask import render_template

from app.models.audit_log import AuditLogRepository
from app.models.ban_user import BanUserRepository
from app.models.company_profile import CompanyProfileRepository
from app.models.parking_establishment import ParkingEstablishmentRepository
from app.models.user import UserRepository
from app.tasks import send_mail


# pylint: disable=C0116


class AdminService:
    """Service class for admin operations."""
    @staticmethod
    def get_user(user_id: int) -> dict:
        """Get user information."""
        return UserManagementService.get_user(user_id)

    @staticmethod
    def ban_user(ban_data: dict, admin_id) -> int:
        return UserBanningService.ban_user(ban_data, admin_id)

    @staticmethod
    def unban_user(user_id: int, admin_id: int, ip_address: str) -> int:
        return UserBanningService.unban_user(user_id, admin_id, ip_address)
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
    def ban_user(ban_data: dict, admin_id) -> int:
        """Ban a user."""
        user_id = BanUserRepository.ban_user(ban_data)
        user_email = UserRepository.get_user(user_id)['email']
        ban_template = render_template(
            '/ban.html', reason=ban_data['reason'], email=user_email
        )
        send_mail(user_email, ban_template, 'You have been banned')
        return AuditLogRepository.create_audit_log({
            "action_type": "CREATE",
            "performed_by": admin_id,
            "target_user": ban_data['user_id'],
            "details": f"User with user_id {ban_data['user_id']} has been banned.",
            "performed_at": datetime.now(pytz.timezone('Asia/Manila')),
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
            "performed_at": datetime.now(pytz.timezone('Asia/Manila')),
            "ip_address": ip_address
        })


class ParkingManagerOperations:
    """Service class for parking applicant operations."""
    @staticmethod
    def get_establishments() -> list:
        """Get all parking establishments."""
        establishments = []
        non_verified_parking_establishments = ParkingEstablishmentRepository.get_establishments()
        if len(non_verified_parking_establishments) == 0:
            return []
        company_profile_ids = [
            parking_establishment['profile_id']
            for parking_establishment in non_verified_parking_establishments
        ]
        company_profiles = CompanyProfileRepository.get_company_profiles(
            profile_ids=company_profile_ids
        )
        for establishment in non_verified_parking_establishments:
            profile = next((
                profile for profile in company_profiles
                if profile['profile_id'] == establishment['profile_id']
            ), None)
            if profile:
                applicant = {
                    "establishment": establishment,
                    "company_profile": profile
                }
                establishments.append(applicant)
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
        return UserRepository.get_all_users()
