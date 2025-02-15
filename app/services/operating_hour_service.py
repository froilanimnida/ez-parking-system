"""" OperatingHourService module """

# pylint: disable=missing-function-docstring, missing-class-docstring, R0903

from app.models.company_profile import CompanyProfileRepository
from app.models.operating_hour import OperatingHoursRepository
from app.models.parking_establishment import ParkingEstablishmentRepository


class OperatingHourService:

    @staticmethod
    def get_operating_hours(manager_id):
        return GetOperatingHoursService.get_operating_hours(manager_id)

    @staticmethod
    def update_operating_hours(manager_id, operating_hours, is24_7):
        return UpdateOperatingHoursService.update_operating_hours(manager_id, operating_hours, is24_7)


class GetOperatingHoursService:
    """Service class for getting operating hours."""
    @staticmethod
    def get_operating_hours(manager_id: int):
        company_profile_id = CompanyProfileRepository.get_company_profile(
            user_id=manager_id
        ).get("profile_id")
        parking_establishment = ParkingEstablishmentRepository.get_establishment(
            profile_id=company_profile_id)
        operating_hours = OperatingHoursRepository.get_operating_hours(
            parking_establishment.get("establishment_id")
        )
        is_24_7 = parking_establishment.get("is24_7")
        return {
            "operating_hours": operating_hours,
            "is_24_7": is_24_7
        }


class UpdateOperatingHoursService:
    """Service class for updating operating hours."""
    @staticmethod
    def update_operating_hours(manager_id: int, operating_hours: dict, is24_7: bool):
        company_profile_id = CompanyProfileRepository.get_company_profile(
            user_id=manager_id
        ).get("profile_id")
        parking_establishment = ParkingEstablishmentRepository.get_establishment(
            profile_id=company_profile_id)
        parking_establishment_id: int = parking_establishment.get("establishment_id")
        if is24_7:
            OperatingHoursRepository.make_operating_hours_24_7(parking_establishment_id)
            ParkingEstablishmentRepository.update_parking_establishment(establishment_data={
                "is24_7": is24_7}, establishment_id=parking_establishment_id)
        else:
            print(operating_hours)
            OperatingHoursRepository.update_operating_hours(
                parking_establishment_id, operating_hours)
        ParkingEstablishmentRepository.update_parking_establishment(
            {"is24_7": is24_7}, parking_establishment_id)
        return {
            "operating_hours": operating_hours,
            "is_24_7": is24_7
        }
