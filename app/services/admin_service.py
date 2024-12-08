""" Wraps the operations that can be performed by the admin. """

from app.models.ban_user import BanUserRepository


class AdminService:
    """Service class for admin operations."""

    @staticmethod
    def ban_user(ban_data: dict, admin_id) -> None: # pylint: disable=C0116
        return PlateBanningService.ban_user(ban_data)

    @staticmethod
    def unban_user(  # pylint: disable=C0116
        plate_number: str,
    ) -> None:
        return PlateBanningService.unban_user(plate_number)


class PlateBanningService:
    """Service class for banning plate numbers."""

    @staticmethod
    def ban_user(ban_data: dict) -> None:  # pylint: disable=C0116
        return BanUserRepository.ban_user(ban_data)

    @staticmethod
    def unban_user(plate_number: str) -> None:  # pylint: disable=C0116
        return BanUserRepository.unban_user(plate_number)