"""This module contains the classes for handling user authentication operations."""

# pylint disable=R0401

import base64
import time
from base64 import urlsafe_b64encode
from datetime import datetime, timedelta
from hashlib import sha256
from os import getenv, urandom
from uuid import uuid4

from flask import render_template
from flask_jwt_extended import create_access_token, create_refresh_token
from pyotp import TOTP

from app.exceptions.authorization_exceptions import (
    EmailAlreadyTaken,
    ExpiredOTPException,
    IncorrectOTPException,
    EmailNotFoundException,
    PhoneNumberAlreadyTaken,
    RequestNewOTPException,
)
from app.models.user import UserOperations, OTPOperations, UserRepository
from app.utils.email_utility import send_mail


class AuthService:
    """Class to handle user authentication operations."""

    @classmethod
    def create_new_user(cls, registration_data: dict):  # pylint: disable=C0116

    @classmethod
    def login_user(cls, login_data: dict):  # pylint: disable=C0116
        return UserLoginService.login_user(login_data=login_data)

    @classmethod
    def generate_otp(cls, email: str):  # pylint: disable=C0116
        return UserOTPService.generate_otp(email=email)

    @classmethod
    def verify_otp(cls, email: str, otp: str):  # pylint: disable=C0116
        return UserOTPService.verify_otp(email=email, otp=otp)

    @classmethod
    def verify_email(cls, token: str):  # pylint: disable=C0116


class UserLoginService:  # pylint: disable=R0903
    """Class to handle user login operations."""

    @classmethod
    def login_user(cls, login_data: dict):  # pylint: disable=C0116
        email = login_data.get("email")

        is_email_taken = UserOperations.is_email_taken(email=email)  # type: ignore
        if not is_email_taken:
            raise EmailNotFoundException(message="Email not found.")

        user = UserOperations.login_user(email=email)  # type: ignore
        user_email = user
        # Send otp to user to their email by calling the generate_otp method
        return UserOTPService.generate_otp(email=user_email)  # type: ignore


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
        if not isinstance(email, str):
            raise TypeError("Email must be a string.")
        email = email.lower()
        seed = f"{getenv('TOTP_SECRET_KEY')}{int(time.time())}"
        six_digits_otp = TOTP(
            base64.b32encode(bytes.fromhex(seed)).decode("UTF-8"),
            digits=6,
            interval=300,
            digest=sha256,
        ).now()
        otp_expiry: datetime = datetime.now() + timedelta(minutes=5)
        one_time_password_template = render_template(
            template_name_or_list="auth/one-time-password.html",
            otp=six_digits_otp,
            user_name=email,
        )
        data = {"email": email, "otp_secret": six_digits_otp, "otp_expiry": otp_expiry}
        OTPOperations.set_otp(data=data)
        send_mail(
            message=one_time_password_template, email=email, subject="One Time Password"
        )

    @classmethod
    def verify_otp(cls, otp: str, email: str):  # pylint: disable=W0613
        """Function to verify an OTP for a user."""
        retrieved_otp, expiry, user_id, role = OTPOperations.get_otp(email=email)
        if expiry is None or retrieved_otp is None:
            raise RequestNewOTPException("Please request for a new OTP.")
        if datetime.now() > expiry:
            OTPOperations.delete_otp(email=email)
            raise ExpiredOTPException(message="OTP has expired.")
        if retrieved_otp != otp or not otp:
            raise IncorrectOTPException(message="Incorrect OTP.")
        OTPOperations.delete_otp(email=email)
        return user_id, role
