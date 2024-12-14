""" Wraps the operations that can be performed by the admin. """
# pylint: disable=C0116
from app.models.ban_user import BanUserRepository


class AdminService:
    """Service class for admin operations."""

    @staticmethod
    def ban_user(ban_data: dict, admin_id) -> None:
        return PlateBanningService.ban_user(ban_data.update({"admin_id": admin_id}))

    @staticmethod
    def unban_user(plate_number: str, admin_id: int) -> None:
        print(admin_id)
        return PlateBanningService.unban_user(plate_number)

    @staticmethod
    def get_parking_applicants() -> list:
        """Get all parking applicants."""



class PlateBanningService:
    """Service class for banning plate numbers."""

    @staticmethod
    def ban_user(ban_data: dict) -> None:  # pylint: disable=C0116
        return BanUserRepository.ban_user(ban_data)

    @staticmethod
    def unban_user(plate_number: str) -> None:  # pylint: disable=C0116
        return BanUserRepository.unban_user(plate_number)


class ParkingApplicantService:
    """Service class for parking applicant operations."""

    @staticmethod
    def get_parking_applicants() -> list:
        """Get all parking applicants."""
        # non_verified_parking_establishments = ParkingEstablishment
