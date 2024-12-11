"""This module contains the classes for handling user authentication operations."""

# pylint disable=R0401

from tempfile import NamedTemporaryFile
from datetime import datetime, timedelta
from os import path

import pytz
from flask import render_template, current_app
from flask_jwt_extended import create_access_token, create_refresh_token

from app.exceptions.authorization_exceptions import (
    EmailAlreadyTaken, ExpiredOTPException, IncorrectOTPException, PhoneNumberAlreadyTaken,
    RequestNewOTPException,
)
from app.models.address import AddressRepository
from app.models.company_profile import CompanyProfileRepository
from app.models.operating_hour import OperatingHoursRepository
from app.models.parking_establishment import ParkingEstablishmentRepository
from app.models.pricing_plan import PricingPlanRepository
from app.models.user import AuthOperations, OTPOperations, UserRepository
from app.tasks import send_mail
from app.utils.security import generate_otp, generate_token, check_file_size, get_random_string
from app.utils.bucket import R2TransactionalUpload, UploadFile


class AuthService:
    """Class to handle user authentication operations."""
    @staticmethod
    def create_new_user(sign_up_data: dict):
        """Create a new user account."""
        user_registration = UserRegistration()
        return user_registration.create_new_user(sign_up_data)

    @staticmethod
    def verify_email(token: str):  # pylint: disable=C0116
        return EmailVerification.verify_email(token=token)

    @classmethod
    def login_user(cls, login_data: dict):  # pylint: disable=C0116
        return UserLoginService.login_user(login_data)

    @classmethod
    def generate_otp(cls, email: str):  # pylint: disable=C0116
        return UserOTPService.generate_otp(email=email)

    @classmethod
    def verify_otp(cls, email: str, otp: str):  # pylint: disable=C0116
        return UserOTPService.verify_otp(email=email, otp=otp)


class UserLoginService:  # pylint: disable=R0903
    """Class to handle user login operations."""
    @classmethod
    def login_user(cls, login_data: dict):  # pylint: disable=C0116
        email = login_data.get("email")
        role = login_data.get("role")
        user_email = AuthOperations.login_user(email, role).get("email")
        return UserOTPService.generate_otp(email=user_email)


class SessionTokenService:  # pylint: disable=R0903
    """This class is responsible for the session token service."""
    @staticmethod
    def generate_session_token(email, user_id) -> str:
        """This is the function responsible for generating the session token."""
        return create_access_token(identity={"email": email, "user_id": user_id})

    @staticmethod
    def generate_refresh_token(email, user_id) -> str:
        """Generate a refresh token."""
        return create_refresh_token(identity={"email": email, "user_id": user_id})


class UserOTPService:
    """Class to handle user OTP operations."""

    @classmethod
    def generate_otp(cls, email: str):
        """Function to generate an OTP for a user."""
        otp_code, otp_expiry = generate_otp()
        one_time_password_template = render_template(
            template_name_or_list="auth/one-time-password.html", otp=otp_code, user_name=email,
        )
        OTPOperations.set_otp({"email": email, "otp_secret": otp_code, "otp_expiry": otp_expiry})
        send_mail(message=one_time_password_template, email=email, subject="One Time Password")

    @classmethod
    def verify_otp(cls, otp: str, email: str) -> tuple[int, str]:
        """
        Verify OTP for a user.

        Args:
            otp: The OTP to verify
            email: User's email

        Returns:
            tuple: (user_id, role)

        Raises:
            RequestNewOTPException: If OTP not found
            ExpiredOTPException: If OTP expired
            IncorrectOTPException: If OTP incorrect
        """
        res = OTPOperations.get_otp(email=email)
        user_id = res.get("user_id")
        role = res.get("role")
        retrieved_otp = res.get("otp_secret")
        expiry_str = res.get("otp_expiry")

        if not retrieved_otp or not expiry_str:
            raise RequestNewOTPException("Please request for a new OTP.")

        expiry = datetime.fromisoformat(expiry_str)
        current_time = datetime.now(pytz.UTC) if expiry.tzinfo else datetime.now()

        if current_time > expiry:
            OTPOperations.delete_otp(email=email)
            raise ExpiredOTPException(message="OTP has expired.")

        if retrieved_otp != otp or not otp:
            raise IncorrectOTPException(message="Incorrect OTP.")

        OTPOperations.delete_otp(email=email)
        return user_id, role


class UserRegistration:  # pylint: disable=R0903
    """User Registration Service"""

    def create_new_user(self, sign_up_data: dict):
        """Create a new user account."""
        NOW = datetime.now()  # pylint: disable=C0103
        user_email = sign_up_data.get("email")
        role = sign_up_data.get("role")
        UserRepository.is_field_taken("email", user_email, EmailAlreadyTaken)
        UserRepository.is_field_taken(
            "phone_number", sign_up_data.get("phone_number"), PhoneNumberAlreadyTaken
        )
        verification_token = generate_token()
        template = render_template(
            "auth/onboarding.html",
            verification_url=f"""
            {current_app.config["FRONTEND_URL"]}/auth/verify-email/{verification_token}
            """
        )
        sign_up_data.update({
            "is_verified": False,
            "created_at": NOW,
            "verification_token": verification_token,
            "verification_expiry": NOW + timedelta(days=7),
        })
        user_id = UserRepository.create_user(sign_up_data)
        if role == "parking_manager":
            owner_type = sign_up_data.get("owner_type")
            company_profile = {
                "profile_id": user_id,
                "owner_type": owner_type,
                "tin": sign_up_data.get("tin"),
                "created_at": NOW,
                "updated_at": NOW,
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
                "created_at": NOW,
                "updated_at": NOW,
            })
            address_id = self.add_new_address({
                "profile_id": company_profile_id,
                "street": sign_up_data.get("street"),
                "barangay": sign_up_data.get("barangay"),
                "city": sign_up_data.get("city"),
                "province": sign_up_data.get("province"),
                "postal_code": sign_up_data.get("postal_code"),
                "created_at": NOW,
                "updated_at": NOW,
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
                "created_at": NOW,
                "updated_at": NOW,
            })
            pricing_plan_id = self.add_pricing_plan(
                parking_establishment_id, sign_up_data.get("pricing_plan")
            )
            print(parking_establishment_id, pricing_plan_id, address_id)
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

    @staticmethod
    def upload_to_bucket(request: dict) -> dict:
        """Upload a file to the bucket."""
        check_file_size(request)
        documents = []
        temp_files = []
        upload_files = []
        for key, file in request.files.items():
            filename_parts = path.splitext(file.filename)
            unique_filename = f"{get_random_string()[:8]}_{filename_parts[0]}{filename_parts[1]}"

            with NamedTemporaryFile(delete=False) as temp_file:
                temp_files.append(temp_file.name)
                file.save(temp_file.name)

            destination_key = unique_filename
            r2_url = f"""
            https://{current_app.config['R2_BUCKET_NAME']}.
            {current_app.config['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com/{destination_key}
            """

            upload_files.append(UploadFile(
                file_path=temp_file.name,
                destination_key=destination_key,
                content_type=file.content_type
            ))

            documents.append({
                "name": key,
                "file_url": r2_url,
                "original_filename": file.filename,
                "stored_filename": unique_filename
            })

        r2_upload = R2TransactionalUpload()
        success, message, details = r2_upload.upload(upload_files)
        print(success, message, details)
        return documents
        # if not success:
        #     return set_response(
        #         400, {"code": "error", "message": "File upload failed", "errors": message}
        #     )


class EmailVerification:  # pylint: disable=R0903
    """Email Verification Service"""

    @staticmethod
    def verify_email(token: str):
        """Verify the email."""
        return UserRepository.verify_email(token)
