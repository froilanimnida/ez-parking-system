"""" OperatingHourService module """

from app.models.company_profile import CompanyProfileRepository
from app.models.operating_hour import OperatingHoursRepository
from app.models.parking_establishment import ParkingEstablishmentRepository


class OperatingHourService:
    
    @staticmethod
    def get_operating_hours(manager_id):
        return GetOperatingHoursService.get_operating_hours(manager_id)
    
    @staticmethod
    def update_operating_hours(manager_id, operating_hours):
        pass
    
    
class GetOperatingHoursService:
    @staticmethod
    def get_operating_hours(manager_id: int):
        company_profile_id = CompanyProfileRepository.get_company_profile(user_id=manager_id).get("profile_id")
        parking_establishment_id = ParkingEstablishmentRepository.get_establishment(
            profile_id=company_profile_id
        ).get("establishment_id")
        return OperatingHoursRepository.get_operating_hours(parking_establishment_id)
    

class UpdateOperatingHoursService:
    pass
