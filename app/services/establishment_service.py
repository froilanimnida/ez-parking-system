""" Establishment related operations from the routes will be handled here. """

from datetime import datetime

from app.models.operating_hour import OperatingHoursRepository
from app.models.parking_establishment import (
    GetEstablishmentOperations,
    UpdateEstablishmentOperations, ParkingEstablishmentRepository,
)
from app.models.parking_slot import ParkingSlotRepository
from app.models.payment_method import PaymentMethodRepository
from app.models.pricing_plan import PricingPlanRepository


class EstablishmentService:
    """Class for operations related to parking establishment."""

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
    def get_establishment(cls, establishment_uuid: bytes):
        """Get parking establishment information."""
        return GetEstablishmentService.get_establishment(establishment_uuid)

    @classmethod
    def get_schedule_hours(cls, manager_id: int):
        """Get parking establishment schedule."""
        return GetEstablishmentService.get_schedule_hours(manager_id)


class GetEstablishmentService:
    """Class for operations related to getting parking establishment."""

    @classmethod
    def get_establishments(cls, query_dict: dict) -> list:
        """
        Get establishments with optional filtering and sorting
        """
        return GetEstablishmentOperations.get_establishments(query_dict)

    @classmethod
    def get_establishment(cls, establishment_uuid: bytes):
        """Get parking establishment information."""
        establishment = ParkingEstablishmentRepository.get_establishment(establishment_uuid=establishment_uuid)
        establishment_id = establishment.get("establishment_id")
        establishment_slots = ParkingSlotRepository.get_slots(establishment_id=establishment_id)
        pricing_plan = PricingPlanRepository.get_pricing_plans(establishment_id)
        payment_methods = PaymentMethodRepository.get_payment_methods(establishment_id)
        operating_hour = OperatingHoursRepository.get_operating_hours(establishment_id)
        return {
            "establishment": establishment,
            "establishment_slots": establishment_slots,
            "pricing_plan": pricing_plan,
            "payment_methods": payment_methods,
            "operating_hour": operating_hour,
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
    