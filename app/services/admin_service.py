""" Wraps the operations that can be performed by the admin. """

from app.models.ban_user import BannedPlateOperations, BanUserRepository


class AdminService:
    """Service class for admin operations."""

    @staticmethod
    def ban_plate_number(ban_data: dict,) -> None: # pylint: disable=C0116
        return PlateBanningService.ban_plate_number(ban_data)

    @staticmethod
    def unban_plate_number(  # pylint: disable=C0116
        plate_number: str,
    ) -> None:
        return PlateBanningService.unban_plate_number(plate_number)


class PlateBanningService:
    """Service class for banning plate numbers."""

    @staticmethod
    def ban_plate_number(ban_data: dict) -> None:  # pylint: disable=C0116
        return BanUserRepository.ban_user(ban_data)

    @staticmethod
    def unban_plate_number(  # pylint: disable=C0116
        plate_number: str,
    ) -> None:
        return BannedPlateOperations.unban_plate(plate_number)