""" Wraps user authentication and registration services. """

from datetime import datetime, timedelta
from base64 import urlsafe_b64encode
from os import getenv, urandom

from flask import render_template

from app.exceptions.authorization_exceptions import (
    EmailAlreadyTaken,
    PhoneNumberAlreadyTaken,
)
from app.models.user import UserRepository
from app.tasks import send_mail


class UserAuth:
    """User Authentication Service"""

    @staticmethod
    def create_new_user(sign_up_data: dict):
        """Create a new user account."""
        return UserRegistration.create_new_user(sign_up_data)

    @staticmethod
    def verify_email(token: str):  # pylint: disable=C0116
        return EmailVerification.verify_email(token=token)


class UserRegistration:  # pylint: disable=R0903
    """User Registration Service"""

    @staticmethod
    def create_new_user(sign_up_data: dict):
        """Create a new user account."""
        user_email = sign_up_data.get("email")
        role = sign_up_data.get("role")
        UserRepository.is_field_taken("email", user_email, EmailAlreadyTaken)
        UserRepository.is_field_taken(
            "phone_number", sign_up_data.get("phone_number"), PhoneNumberAlreadyTaken
        )
        verification_token = urlsafe_b64encode(urandom(128)).decode("utf-8").rstrip("=")
        is_production = getenv("ENVIRONMENT") == "production"
        base_url = (
            getenv("PRODUCTION_URL") if is_production else getenv("DEVELOPMENT_URL")
        )
        verification_url = f"{base_url}/auth/verify-email/{verification_token}"
        template = render_template(
            "auth/onboarding.html", verification_url=verification_url
        )
        sign_up_data.update(
            {
                "is_verified": False,
                "created_at": datetime.now(),
                "verification_token": verification_token,
                "verification_expiry": datetime.now() + timedelta(days=7),
            }
        )
        user_id = UserRepository.create_user(sign_up_data)
        if role == "parking_manager":
            owner_type = sign_up_data.get("owner_type")
            if owner_type == "individual":
                pass
            elif owner_type == "company":
                pass
        return send_mail(user_email, template, "Welcome to EZ Parking")


class EmailVerification:  # pylint: disable=R0903
    """Email Verification Service"""

    @staticmethod
    def verify_email(token: str):
        """Verify the email."""
        return UserRepository.verify_email(token)
