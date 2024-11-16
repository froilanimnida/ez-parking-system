""" Establishment related operations from the routes will be handled here. """

from datetime import datetime
from uuid import uuid4

from app.models.parking_establishment import (
    CreateEstablishmentOperations,
    GetEstablishmentOperations,
    UpdateEstablishmentOperations,
    DeleteEstablishmentOperations,
)


class EstablishmentService:
    """Class for operations related to parking establishment."""

    @classmethod
    def create_new_parking_establishment(cls, establishment_data: dict):
        """Create a new parking establishment."""
        CreateEstablishmentService.create_new_parking_establishment(establishment_data)
    @classmethod
    def get_establishments(cls, query_dict: dict,) -> list:
        """
        Get establishments with optional filtering and sorting
        """
        return GetEstablishmentService.get_establishments(query_dict=query_dict)
    @classmethod
    def get_establishment_by_id(cls, establishment_id: int):
        """Get parking establishment by ID."""
        return GetEstablishmentService.get_establishment_by_id(establishment_id)
    @classmethod
    def update_establishment(cls, establishment_id: int, establishment_data: dict):
        """Update parking establishment."""
        UpdateEstablishmentService.update_establishment(
            establishment_id, establishment_data
        )
    @classmethod
    def delete_establishment(cls, establishment_id: int):
        """Delete parking establishment."""
        DeleteEstablishmentService.delete_establishment(establishment_id)


class CreateEstablishmentService:  # pylint: disable=R0903
    """Class for operations related to creating parking establishment."""
    @classmethod
    def create_new_parking_establishment(cls, establishment_data: dict):
        """Create a new parking establishment."""
        new_parking_establishment_uuid = uuid4().bytes
        establishment_data["uuid"] = new_parking_establishment_uuid
        establishment_data["created_at"] = datetime.now()
        establishment_data["updated_at"] = datetime.now()
        CreateEstablishmentOperations.create_establishment(establishment_data)

class GetEstablishmentService:
    """Class for operations related to getting parking establishment."""
    @classmethod
    def get_establishments(cls, query_dict: dict) -> list:
        """
        Get establishments with optional filtering and sorting
        """
        return GetEstablishmentOperations.get_establishments(query_dict)

    @classmethod
    def get_establishment_by_id(cls, establishment_id: int):
        """Get parking establishment by ID. This is the overview of the parking establishment."""
        return GetEstablishmentOperations.get_establishment_by_id(establishment_id)

class UpdateEstablishmentService:  # pylint: disable=R0903
    """Class for operations related to updating parking establishment."""
    @classmethod
    def update_establishment(cls, establishment_id: int, establishment_data: dict):
        """Update parking establishment."""
        establishment_data["updated_at"] = datetime.now()
        UpdateEstablishmentOperations.update_establishment(
            establishment_id, establishment_data
        )


class DeleteEstablishmentService:  # pylint: disable=R0903
    """Class for operations related to deleting parking establishment."""
    @classmethod
    def delete_establishment(cls, establishment_id: int):
        """Delete parking establishment."""
        DeleteEstablishmentOperations.delete_establishment(establishment_id)
