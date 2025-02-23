""" This module contains the reports service """

# pylint: disable=missing-function-docstring

from app.models.company_profile import CompanyProfileRepository
from app.models.parking_establishment import ParkingEstablishmentRepository
from app.models.parking_transaction import BusinessIntelligence


class Reports:
    """ Reports class """
    @staticmethod
    def revenue_report(parking_manager_id, start_date, end_date):
        return RevenueReports.get_revenue_report(
            parking_manager_id, start_date, end_date
        )
    @staticmethod
    def occupancy_report(user_id):
        return RevenueReports.get_occupancy_report(user_id)
class RevenueReports:
    """ Revenue report class """
    @staticmethod
    def get_revenue_report(parking_manager_id, start_date, end_date):
        company_profile_id = CompanyProfileRepository.get_company_profile(
            user_id=parking_manager_id
        ).get("profile_id")
        parking_establishment_id = ParkingEstablishmentRepository.get_establishment(
            profile_id=company_profile_id
        ).get("establishment_id")
        return BusinessIntelligence.get_revenue_analysis(
            establishment_id=parking_establishment_id,
            start_date=start_date,
            end_date=end_date
        )
    @staticmethod
    def get_occupancy_report(parking_manager_id):
        company_profile_id = CompanyProfileRepository.get_company_profile(
            user_id=parking_manager_id
        ).get("profile_id")
        parking_establishment_id = ParkingEstablishmentRepository.get_establishment(
            profile_id=company_profile_id
        ).get("establishment_id")
        return BusinessIntelligence.get_occupancy_rate(
            establishment_id=parking_establishment_id
        )
