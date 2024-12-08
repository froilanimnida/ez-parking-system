""" Wraps user authentication and registration services. """

from base64 import urlsafe_b64encode
from datetime import datetime, timedelta
from os import getenv, urandom

from flask import render_template

from app.exceptions.authorization_exceptions import (
    EmailAlreadyTaken,
    PhoneNumberAlreadyTaken,
)
from app.models.address import AddressRepository
from app.models.company_profile import CompanyProfileRepository
from app.models.operating_hour import OperatingHoursRepository
from app.models.parking_establishment import ParkingEstablishmentRepository
from app.models.pricing_plan import PricingPlanRepository
from app.models.user import UserRepository
from app.tasks import send_mail


class UserAuth:
    """User Authentication Service"""

    @staticmethod
    def create_new_user(sign_up_data: dict):
        """Create a new user account."""
        user_registration = UserRegistration()
        return user_registration.create_new_user(sign_up_data)

    @staticmethod
    def verify_email(token: str):  # pylint: disable=C0116
        return EmailVerification.verify_email(token=token)


class UserRegistration:  # pylint: disable=R0903
    """User Registration Service"""

    def create_new_user(self, sign_up_data: dict):
        """Create a new user account."""
        user_email = sign_up_data.get("email")
        role = sign_up_data.get("role")
        UserRepository.is_field_taken("email", user_email, EmailAlreadyTaken)
        UserRepository.is_field_taken(
            "phone_number", sign_up_data.get("phone_number"), PhoneNumberAlreadyTaken
        )
        verification_token = urlsafe_b64encode(urandom(128)).decode("utf-8").rstrip("=")
        is_production = getenv("ENVIRONMENT") == "production"
        base_url = (getenv("PRODUCTION_URL") if is_production else getenv("DEVELOPMENT_URL"))
        template = render_template(
            "auth/onboarding.html",
            verification_url=f"{base_url}/auth/verify-email/{verification_token}"
        )
        sign_up_data.update({
            "is_verified": False,
            "created_at": datetime.now(),
            "verification_token": verification_token,
            "verification_expiry": datetime.now() + timedelta(days=7),
        })
        user_id = UserRepository.create_user(sign_up_data)
        if role == "parking_manager":
            owner_type = sign_up_data.get("owner_type")
            company_profile = {
                "profile_id": user_id,
                "owner_type": owner_type,
                "tin": sign_up_data.get("tin"),
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }
            if owner_type == "company":
                company_profile.update({
                    "company_name": sign_up_data.get("company_name"),
                    "company_reg_number": sign_up_data.get("company_reg_number"),
                })
            company_profile_id = CompanyProfileRepository.create_new_company_profile({
                "profile_id": user_id,
                "owner_type": owner_type,
                "company_name": sign_up_data.get("company_name"),
                "company_reg_number": sign_up_data.get("company_reg_number"),
                "tin": sign_up_data.get("tin"),
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            })
            address_id = self.add_new_address({
                "profile_id": company_profile_id,
                "street": sign_up_data.get("street"),
                "barangay": sign_up_data.get("barangay"),
                "city": sign_up_data.get("city"),
                "province": sign_up_data.get("province"),
                "postal_code": sign_up_data.get("postal_code"),
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            })
            parking_establishment_id = self.add_new_parking_establishment({
                "profile_id": company_profile_id,
                "space_type": sign_up_data.get("space_type"),
                "space_layout": sign_up_data.get("space_layout"),
                "custom_layout": sign_up_data.get("custom_layout"),
                "dimension": sign_up_data.get("dimension"),
                "is_24_hours": sign_up_data.get("is_24_hours"),
                "access_info": sign_up_data.get("access_info"),
                "custom_access_info": sign_up_data.get("custom_access_info"),
                "status": "pending",
                "lighting": sign_up_data.get("lighting"),
                "accessibility": sign_up_data.get("accessibility"),
                "nearby_landmarks": sign_up_data.get("nearby_landmarks"),
                "longitude": sign_up_data.get("longitude"),
                "latitude": sign_up_data.get("latitude"),
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            })
            pricing_plan_id = self.add_pricing_plan(
                parking_establishment_id, sign_up_data.get("pricing_plan")
            )
            self.add_operating_hours(parking_establishment_id, sign_up_data.get("operating_hours"))
        return send_mail(user_email, template, "Welcome to EZ Parking")
    
    @staticmethod
    def add_new_address(address_data: dict):
        """Add a new address."""
        return AddressRepository.create_address(address_data)
    
    @staticmethod
    def add_new_parking_establishment(establishment_data: dict):
        """Add a new parking establishment."""
        return ParkingEstablishmentRepository.create_establishment(establishment_data)
    
    @staticmethod
    def add_operating_hours(establishment_id: int, operating_hours: dict):
        """Add operating hours for a parking establishment."""
        return OperatingHoursRepository.create_operating_hours(establishment_id, operating_hours)
    
    @staticmethod
    def add_pricing_plan(establisment_id: int, pricing_plan_data: dict):
        """Add a pricing plan."""
        return PricingPlanRepository.create_pricing_plan(establisment_id, pricing_plan_data)


class EmailVerification:  # pylint: disable=R0903
    """Email Verification Service"""

    @staticmethod
    def verify_email(token: str):
        """Verify the email."""
        return UserRepository.verify_email(token)
