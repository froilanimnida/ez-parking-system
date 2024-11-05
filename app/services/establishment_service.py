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
    def get_establishment_by_id(cls, establishment_id: int):
        """Get parking establishment by ID."""
        return GetEstablishmentService.get_establishment_by_id(establishment_id)

    @classmethod
    def get_all_establishments(cls):
        """Get all parking establishments."""
        return GetEstablishmentService.get_all_establishments()

    @classmethod
    def get_nearest_establishments(cls, latitude: float, longitude: float):
        """Get nearest parking establishments based on the current user location."""
        return GetEstablishmentService.get_nearest_establishments(latitude, longitude)

    @classmethod
    def get_24_hours_establishments(cls):
        """Get parking establishments that are open 24 hours."""
        return GetEstablishmentService.get_24_hours_establishments()

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
        CreateEstablishmentOperations.create_establishment(establishment_data)


class GetEstablishmentService:
    """Class for operations related to getting parking establishment."""

    @classmethod
    def get_all_establishments(cls):
        """Get all parking establishments."""
        return GetEstablishmentOperations.get_all_establishments()

    @classmethod
    def get_establishment_by_id(cls, establishment_id: int):
        """Get parking establishment by ID."""
        return GetEstablishmentOperations.get_establishment_by_id(establishment_id)

    @classmethod
    def get_nearest_establishments(cls, latitude: float, longitude: float):
        """Get nearest parking establishments based on the current user location."""
        return GetEstablishmentOperations.get_nearest_establishments(
            latitude, longitude
        )

    @classmethod
    def get_24_hours_establishments(cls):
        """Get parking establishments that are open 24 hours."""
        return GetEstablishmentOperations.get_24_hours_establishments()


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
