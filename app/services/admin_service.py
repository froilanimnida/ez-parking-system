""" Wraps the operations that can be performed by the admin. """

from datetime import datetime

from app.models.ban_user import BannedPlateOperations, BanUserRepository
from app.models.slot import SlotOperation


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

    @staticmethod
    def add_slot(slot_data: dict) -> None:  # pylint: disable=C0116
        return SlotService.add_slot(slot_data)

    @staticmethod
    def update_parking_slot(slot_data: dict) -> None:  # pylint: disable=C0116
        return SlotService.update_slot(slot_data)


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


class SlotService:
    """Service class for slot operations."""

    @staticmethod
    def add_slot(slot_data: dict) -> None:  # pylint: disable=C0116
        slot_data["created_at"] = datetime.now()
        slot_data["updated_at"] = datetime.now()
        return SlotOperation.create_slot(slot_data)

    @staticmethod
    def update_slot(slot_data: dict) -> None:  # pylint: disable=C0116
        slot_data["updated_at"] = datetime.now()
        slot_id = slot_data.pop("slot_id")
        return SlotOperation.update_slot(slot_id, slot_data, is_admin=True)
