""" Establishment related operations from the routes will be handled here. """

from datetime import datetime
from uuid import uuid4

from app.models.parking_establishment import (
    CreateEstablishmentOperations,
    GetEstablishmentOperations,
    UpdateEstablishmentOperations,
    DeleteEstablishmentOperations,
)
from app.models.slot import GettingSlotsOperations


class EstablishmentService:
    """Class for operations related to parking establishment."""

    @classmethod
    def create_new_parking_establishment(cls, establishment_data: dict):
        """Create a new parking establishment."""
        CreateEstablishmentService.create_new_parking_establishment(establishment_data)

    @classmethod
    def get_establishments(cls, query_dict: dict) -> list:
        """
        Get establishments with optional filtering and sorting
        """
        return GetEstablishmentService.get_establishments(query_dict=query_dict)

    @classmethod
    def update_establishment(cls, establishment_data: dict):
        """Update parking establishment."""
        UpdateEstablishmentService.update_establishment(establishment_data)

    @classmethod
    def delete_establishment(cls, establishment_uuid: bytes):
        """Delete parking establishment."""
        DeleteEstablishmentService.delete_establishment(establishment_uuid)

    @classmethod
    def get_establishment_info(cls, establishment_uuid: bytes):
        """Get parking establishment information."""
        return GetEstablishmentService.get_establishment_info(establishment_uuid)

    @classmethod
    def get_schedule_hours(cls, manager_id: int):
        """Get parking establishment schedule."""
        return GetEstablishmentService.get_schedule_hours(manager_id)

    @classmethod
    def update_establishment_schedule(cls, manager_id: int, schedule_data: dict):
        """Update parking establishment schedule."""
        return UpdateEstablishmentService.update_establishment_schedule(
            manager_id, schedule_data
        )


class CreateEstablishmentService:  # pylint: disable=R0903
    """Class for operations related to creating parking establishment."""

    @classmethod
    def create_new_parking_establishment(cls, establishment_data: dict):
        """Create a new parking establishment."""
        establishment_data["uuid"] = uuid4().bytes
        establishment_data["created_at"] = datetime.now()
        establishment_data["updated_at"] = datetime.now()
        return CreateEstablishmentOperations.create_establishment(establishment_data)


class GetEstablishmentService:
    """Class for operations related to getting parking establishment."""

    @classmethod
    def get_establishments(cls, query_dict: dict) -> list:
        """
        Get establishments with optional filtering and sorting
        """
        return GetEstablishmentOperations.get_establishments(query_dict)

    @classmethod
    def get_establishment_info(cls, establishment_uuid_bin: bytes):
        """Get parking establishment information."""
        establishment_info = GetEstablishmentOperations.get_establishment_info(
            establishment_uuid_bin
        )
        establishment_slots = GettingSlotsOperations.get_all_slots(
            establishment_info.get("establishment_id")
        )
        return {
            "establishment_info": establishment_info,
            "establishment_slots": establishment_slots,
        }

    @classmethod
    def get_schedule_hours(cls, manager_id: int):
        """Get parking establishment schedule."""
        return GetEstablishmentOperations.get_establishment_schedule(manager_id)


class UpdateEstablishmentService:  # pylint: disable=R0903
    """Class for operations related to updating parking establishment."""

    @classmethod
    def update_establishment(cls, establishment_data: dict):
        """Update parking establishment."""
        establishment_data["updated_at"] = datetime.now()
        UpdateEstablishmentOperations.update_establishment(establishment_data)

    @classmethod
    def update_establishment_schedule(cls, manager_id: int, schedule_data: dict):
        """Update parking establishment schedule."""
        return UpdateEstablishmentOperations.update_hours(manager_id, schedule_data)


class DeleteEstablishmentService:  # pylint: disable=R0903
    """Class for operations related to deleting parking establishment."""

    @classmethod
    def delete_establishment(cls, establishment_uuid: bytes):
        """Delete parking establishment."""
        DeleteEstablishmentOperations.delete_establishment(establishment_uuid)
