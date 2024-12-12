"""This module contains the classes for handling user authentication operations."""

# pylint disable=R0401

from datetime import datetime, timedelta
from os import path
from tempfile import NamedTemporaryFile

import pytz
from flask import render_template, current_app
from flask_jwt_extended import create_access_token, create_refresh_token

from app.exceptions.authorization_exceptions import (
    EmailAlreadyTaken, ExpiredOTPException, IncorrectOTPException, PhoneNumberAlreadyTaken,
    RequestNewOTPException,
)
from app.models.address import AddressRepository
from app.models.company_profile import CompanyProfileRepository
from app.models.establishment_document import EstablishmentDocumentRepository
from app.models.operating_hour import OperatingHoursRepository
from app.models.parking_establishment import ParkingEstablishmentRepository
from app.models.payment_method import PaymentMethodRepository
from app.models.pricing_plan import PricingPlanRepository
from app.models.user import AuthOperations, OTPOperations, UserRepository
from app.tasks import send_mail
from app.utils.bucket import R2TransactionalUpload, UploadFile
from app.utils.security import generate_otp, generate_token, get_random_string


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
        user_email = AuthOperations.login_user(email).get("email")
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
        user_data = sign_up_data.get("user", {})

        UserRepository.is_field_taken(
            "email", sign_up_data.get("user", {}).get("email"), EmailAlreadyTaken
        )
        UserRepository.is_field_taken(
            "phone_number",
            sign_up_data.get("user", {}).get("phone_number"),
            PhoneNumberAlreadyTaken
        )
        verification_token = generate_token()
        template = render_template(
            "auth/onboarding.html",
            verification_url=f"""
            {current_app.config["FRONTEND_URL"]}/auth/verify-email/{verification_token}
            """
        )
        user_data.update({
            "is_verified": False,
            "verification_token": verification_token,
            "verification_expiry": datetime.now() + timedelta(days=7),
        })
        user_id = UserRepository.create_user(user_data)
        if sign_up_data.get("user", {}).get("role") == "parking_manager":
            company_profile = sign_up_data.get("company_profile", {})
            company_profile.update({"profile_id": user_id,})
            company_profile_id = self.add_new_company_profile(company_profile)

            address = sign_up_data.get("address", {})
            address.update({"profile_id": company_profile_id,})
            self.add_new_address(address)

            parking_establishment = sign_up_data.get("parking_establishment", {})
            parking_establishment.update({"profile_id": company_profile_id})
            parking_establishment_id = self.add_new_parking_establishment(parking_establishment)

            pricing_plan = sign_up_data.get("pricing_plan", {})
            self.add_pricing_plan(parking_establishment_id, pricing_plan)

            payment_method = sign_up_data.get("payment_method", {})
            payment_method.update({"establishment_id": parking_establishment_id})
            self.add_payment_method(payment_method)

            operating_hours = sign_up_data.get("operating_hour", {})
            self.add_operating_hours(parking_establishment_id, operating_hours)

            documents = sign_up_data.get("documents", [])
            self.add_establishment_documents(parking_establishment_id, documents)

        return send_mail(
                sign_up_data.get("user", {}).get("email"), template, "Welcome to EZ Parking"
            )

    @staticmethod
    def add_new_address(address_data: dict):
        """Add a new address."""
        return AddressRepository.create_address(address_data)

    @staticmethod
    def add_new_parking_establishment(establishment_data: dict):
        """Add a new parking establishment."""
        return ParkingEstablishmentRepository.create_establishment(establishment_data)

    @staticmethod
    def add_pricing_plan(establishment_id: int, pricing_plan_data: dict):
        """Add pricing plans for a parking establishment."""
        pricing_plans = []
        for rate_type, plan in pricing_plan_data.items(): # pylint: disable=W0612
            pricing_plans.append({
                'rate_type': plan['rate_type'],
                'is_enabled': bool(plan['is_enabled']),
                'rate': float(plan['rate'])
            })

        return PricingPlanRepository.create_pricing_plan(establishment_id, pricing_plans)

    @staticmethod
    def add_new_company_profile(company_profile_data: dict):
        """Add a new company profile."""
        return CompanyProfileRepository.create_new_company_profile(company_profile_data)

    @staticmethod
    def add_operating_hours(establishment_id: int, operating_hours: dict):
        """Add operating hours for a parking establishment."""
        formatted_hours = {}
        for day, hours in operating_hours.items():
            formatted_hours[day] = {
                'is_enabled': bool(hours.get('enabled')),
                'opening_time': hours.get('open'),
                'closing_time': hours.get('close')
            }
        return OperatingHoursRepository.create_operating_hours(establishment_id, formatted_hours)

    @staticmethod
    def add_payment_method(payment_method_data: dict):
        """Add payment methods."""
        return PaymentMethodRepository.create_payment_method(payment_method_data)
    @staticmethod
    def add_establishment_documents(
         establishment_id: int, documents: list
    ):  # pylint: disable=too-many-locals
        """Add establishment documents."""
        r2_client = R2TransactionalUpload()
        upload_files = []

        for doc in documents:
            print(doc)
            file = doc['file']
            doc_type = doc['type'].lower()

            unique_id = get_random_string()[:8]
            base_name = path.splitext(file.filename)[0]
            extension = path.splitext(file.filename)[1]
            unique_filename = f"{unique_id}_{base_name}{extension}"

            with NamedTemporaryFile(delete=False) as temp_file:
                file.save(temp_file.name)
                upload_files.append(UploadFile(
                    file_path=temp_file.name,
                    destination_key=f"establishments/{establishment_id}/{unique_filename}",
                    content_type=file.content_type
                ))

            doc_type_map = {
                'gov_id': 'gov_id',
                'parking_photo': 'parking_photos',
                'proof_of_ownership': 'proof_of_ownership',
                'business_cert': 'business_certificate',
                'bir_cert': 'bir_certificate',
                'liability_insurance': 'liability_insurance'
            }

            if doc_type not in doc_type_map:
                raise ValueError(f"Invalid document type: {doc_type}")

            doc_data = {
                'establishment_id': establishment_id,
                'document_type': doc_type_map[doc_type].lower(),
                'bucket_path': f"establishments/{establishment_id}/{unique_filename}",
                'filename': file.filename,
                'mime_type': file.content_type,
                'file_size': file.content_length if hasattr(file, 'content_length') else 0,
                'status': 'pending'
            }
            EstablishmentDocumentRepository.create_establishment_document(doc_data)

        success, message, details = r2_client.upload(upload_files)  # pylint: disable=W0612
        if not success:
            raise Exception(f"Failed to upload documents: {message}")  # pylint: disable=W0719

class EmailVerification:  # pylint: disable=R0903
    """Email Verification Service"""

    @staticmethod
    def verify_email(token: str):
        """Verify the email."""
        return UserRepository.verify_email(token)
