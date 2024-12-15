""" Establishment related operations from the routes will be handled here. """

from typing import overload, Union

from app.models.address import AddressRepository
from app.models.company_profile import CompanyProfileRepository
from app.models.establishment_document import EstablishmentDocumentRepository
from app.models.operating_hour import OperatingHoursRepository
from app.models.parking_establishment import (
    ParkingEstablishmentRepository, GetEstablishmentOperations
)
from app.models.parking_slot import ParkingSlotRepository
from app.models.payment_method import PaymentMethodRepository
from app.models.pricing_plan import PricingPlanRepository


class EstablishmentService:
    """Class for operations related to parking establishment."""

    @classmethod
    def get_establishments(cls, query_dict: dict) -> list:
        """Get establishments with optional filtering and sorting"""
        return GetEstablishmentService.get_establishments(query_dict=query_dict)

    @staticmethod
    @overload
    def get_establishment(establishment_uuid: str) -> dict:
        """Get parking establishment information by UUID."""

    @staticmethod
    @overload
    def get_establishment(manager_id: int) -> dict:
        """Get parking establishment information by manager ID."""

    @staticmethod
    def get_establishment(identifier: Union[str, int]) -> dict:
        """Get parking establishment information."""
        if isinstance(identifier, str):
            return GetEstablishmentService.get_establishment(identifier)
        if isinstance(identifier, int):
            return AdministrativeService.get_establishment(identifier)
        return {}


class GetEstablishmentService:
    """Class for operations related to getting parking establishment."""

    @classmethod
    def get_establishments(cls, query_dict: dict) -> list:
        """Get establishments with optional filtering and sorting"""
        return GetEstablishmentOperations.get_establishments(query_dict)

    @classmethod
    def get_establishment(cls, establishment_uuid: str):
        """Get parking establishment information."""
        parking_establishment_details = ParkingEstablishmentRepository.get_establishment(
            establishment_uuid=establishment_uuid
        )
        parking_establishment_id = parking_establishment_details['establishment_id']
        parking_establishment_operating_hours = OperatingHoursRepository.get_operating_hours(
            establishment_id=parking_establishment_id
        )
        parking_establishment_slot = ParkingSlotRepository.get_slots(
            establishment_id=parking_establishment_id
        )
        parking_establishment_payment_methods = PaymentMethodRepository.get_payment_methods(
            establishment_id=parking_establishment_id
        )
        parking_establishment_pricing_plans = PricingPlanRepository.get_pricing_plans(
            establishment_id=parking_establishment_id
        )
        company_details = CompanyProfileRepository.get_company_profile(
            profile_id=parking_establishment_details['profile_id']
        )
        establishment_documents = EstablishmentDocumentRepository.get_establishment_documents(
            establishment_id=parking_establishment_id
        )
        return {
            "parking_establishment": parking_establishment_details,
            "operating_hours": parking_establishment_operating_hours,
            "slots": parking_establishment_slot,
            "payment_methods": parking_establishment_payment_methods,
            "pricing_plans": parking_establishment_pricing_plans,
            "company_profile": company_details,
            "establishment_documents": establishment_documents
        }


class AdministrativeService:  # pylint: disable=too-few-public-methods
    """Class for operations related to administrative tasks."""
    @classmethod
    def get_establishment(cls, manager_id: int):
        """Get parking establishment information."""
        company_profile = CompanyProfileRepository.get_company_profile(user_id=manager_id)
        company_profile_id = company_profile.get("profile_id")
        address = AddressRepository.get_address(profile_id=company_profile_id)
        parking_establishment = ParkingEstablishmentRepository.get_establishment(
            profile_id=company_profile_id
        )
        establishment_document = EstablishmentDocumentRepository.get_establishment_documents(
            establishment_id=parking_establishment.get("establishment_id")
        )
        operating_hour = OperatingHoursRepository.get_operating_hours(
            parking_establishment.get("establishment_id")
        )
        payment_method = PaymentMethodRepository.get_payment_methods(
            parking_establishment.get("establishment_id")
        )
        pricing_plan = PricingPlanRepository.get_pricing_plans(
            parking_establishment.get("establishment_id")
        )
        return {
            "company_profile": company_profile,
            "address": address,
            "parking_establishment": parking_establishment,
            "establishment_document": establishment_document,
            "operating_hour": operating_hour,
            "payment_method": payment_method,
            "pricing_plan": pricing_plan,
        }
