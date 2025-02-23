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
    @staticmethod
    def peak_hours_report(user_id):
        return RevenueReports.get_peak_hours_report(user_id)
    @staticmethod
    def vehicle_distribution(user_id, start_date, end_date):
        return RevenueReports.get_vehicle_distribution(
            user_id, start_date, end_date
        )
    @staticmethod
    def payment_stats_report(user_id, start_date, end_date):
        return RevenueReports.get_payment_stats_report(
            user_id, start_date, end_date
        )
    @staticmethod
    def utilization_report(user_id, start_date, end_date):
        return RevenueReports.get_utilization_report(
            user_id, start_date, end_date
        )


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
    @staticmethod
    def get_peak_hours_report(parking_manager_id):
        company_profile_id = CompanyProfileRepository.get_company_profile(
            user_id=parking_manager_id
        ).get("profile_id")
        parking_establishment_id = ParkingEstablishmentRepository.get_establishment(
            profile_id=company_profile_id
        ).get("establishment_id")
        return BusinessIntelligence.get_peak_hours_analysis(
            establishment_id=parking_establishment_id
        )
    @staticmethod
    def get_vehicle_distribution(parking_manager_id, start_date, end_date):
        company_profile_id = CompanyProfileRepository.get_company_profile(
            user_id=parking_manager_id
        ).get("profile_id")
        establishment_id = ParkingEstablishmentRepository.get_establishment(
            profile_id=company_profile_id
        ).get("establishment_id")
        return BusinessIntelligence.get_vehicle_type_distribution(
            establishment_id=establishment_id,
            start_date=start_date,
            end_date=end_date
        )
    @staticmethod
    def get_payment_stats_report(parking_manager_id, start_date, end_date):
        company_profile_id = CompanyProfileRepository.get_company_profile(
            user_id=parking_manager_id
        ).get("profile_id")
        establishment_id = ParkingEstablishmentRepository.get_establishment(
            profile_id=company_profile_id
        ).get("establishment_id")
        return BusinessIntelligence.get_payment_analytics(
            establishment_id=establishment_id,
            start_date=start_date,
            end_date=end_date
        )
    @staticmethod
    def get_utilization_report(parking_manager_id, start_date, end_date):
        company_profile_id = CompanyProfileRepository.get_company_profile(
            user_id=parking_manager_id
        ).get("profile_id")
        establishment_id = ParkingEstablishmentRepository.get_establishment(
            profile_id=company_profile_id
        ).get("establishment_id")
        return BusinessIntelligence.get_slot_utilization_by_type(
            establishment_id=establishment_id,
            start_date=start_date,
            end_date=end_date
        )
