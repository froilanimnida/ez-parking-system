"""This module contains the classes for handling user authentication operations."""
import base64
import re
import time
from datetime import datetime, timedelta
from hashlib import sha256
from os import getenv
from re import search
from uuid import uuid4

from flask import render_template
from flask_jwt_extended import create_access_token, create_refresh_token
from pyotp import TOTP

from app.exceptions.authorization_exception import (
    EmailAlreadyTaken, ExpiredOTPException, IncorrectOTPException, MissingFieldsException,
    InvalidEmailException, EmailNotFoundException
)
from app.models.user import UserOperations, OTPOperations
from app.utils.email_utility import send_mail


class AuthService:
    """ Class to handle user authentication operations. """
    @classmethod
    def create_new_user(cls, registration_data: dict) -> str:  # pylint: disable=C0116
        return UserRegistrationService.register_user(user_data=registration_data)

    @classmethod
    def login_user(cls, login_data: dict):  # pylint: disable=C0116
        return UserLoginService.login_user(login_data=login_data)

    @classmethod
    def generate_otp(cls, email: str):  # pylint: disable=C0116
        return UserOTPService.generate_otp(email=email)

    @classmethod
    def verify_otp(cls,  email: str,  otp: str):  # pylint: disable=C0116
        return UserOTPService.verify_otp(email=email, otp=otp)

    @classmethod
    def set_nickname(cls, email, nickname):  # pylint: disable=C0116
        return UserProfileService.set_nickname(email=email,  nickname=nickname)



class UserRegistrationService:
    """ Class to handle user registration operations. """
    @classmethod
    def register_user(cls, user_data: dict) -> str:  # pylint: disable=C0116
        email = user_data.get('email')
        if not email:
            raise MissingFieldsException('Please provide an email address.')

        if not search(r'^[a-z0-9]+[._]?[a-z0-9]+@\w+[.]\w+$', string=email):
            raise InvalidEmailException(
                message='Please provide a valid email address.')

        is_email_taken: bool = UserOperations.is_email_taken(email=email)
        if is_email_taken:
            raise EmailAlreadyTaken(message='Email already taken.')
        phone_number = user_data.get('phone_number')

        username: str = str(object=user_data
                            .get('email')).split(sep='@', maxsplit=1)[0]
        first_name = user_data.get('first_name')
        last_name = user_data.get('last_name')
        role = 'user'
        uuid: bytes = uuid4().bytes
        if not first_name or not last_name:
            raise MissingFieldsException(
                message='Please provide all the required fields.')
        user_data = {
            'uuid': uuid,
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'phone_number': phone_number,
            'role': role
        }
        return UserOperations.create_new_user(user_data=user_data)


class UserLoginService:
    """ Class to handle user login operations. """
    @classmethod
    def login_user(cls, login_data: dict):  # pylint: disable=C0116
        email = login_data.get('email')
        if not email:
            raise MissingFieldsException(
                message='Please provide an email address.')

        is_email_taken = UserOperations.is_email_taken(email=email)
        if not is_email_taken:
            raise EmailNotFoundException(message='Email not found.')

        if not re.search(pattern=r'^[a-z0-9]+[._]?[a-z0-9]+@\w+[.]\w+$', string=email):
            raise InvalidEmailException(
                'Please provide a valid email address.')
        user = UserOperations.login_user(email=email)
        user_email = user
        # Send otp to user to their email by calling the generate_otp method
        return UserOTPService.generate_otp(email=user_email) # type: ignore


class SessionTokenService:  # pylint: disable=R0903
    """ This class is responsible for the session token service. """
    @staticmethod
    def generate_session_token(email, user_id) -> str:
        """This is the function responsible for generating the session token."""
        return create_access_token(identity={'email': email, 'user_id': user_id})

    @staticmethod
    def generate_refresh_token(email, user_id) -> str:
        """Generate a refresh token. """
        return create_refresh_token(identity={'email': email, 'user_id': user_id})


class UserOTPService:
    """ Class to handle user OTP operations. """
    @classmethod
    def generate_otp(cls, email: str):
        """ Function to generate an OTP for a user. """
        seed = f"{getenv('TOTP_SECRET_KEY')}{int(time.time())}"
        six_digits_otp = TOTP(base64.b32encode(bytes.fromhex(seed))
                              .decode('UTF-8'),
                              digits=6, interval=300, digest=sha256).now()
        otp_expiry: datetime = datetime.now() + timedelta(minutes=5)
        one_time_password_template = render_template(
            template_name_or_list='auth/one-time-password.html',
            otp=six_digits_otp,
            user_name=email
        )
        data: dict[str, str | datetime] = {
            'email': email,
            'otp_secret': six_digits_otp,
            'otp_expiry': otp_expiry
        }
        OTPOperations.set_otp(data=data)
        send_mail(message=one_time_password_template, email=email, subject="One Time Password")

    @classmethod
    def verify_otp(cls, otp: str, email: str):  # pylint: disable=W0613
        """ Function to verify an OTP for a user. """
        retrieved_otp, expiry, user_id = OTPOperations.get_otp(email=email)
        if datetime.now() > expiry:
            raise ExpiredOTPException(message='OTP has expired.')
        if retrieved_otp != otp or not otp:
            raise IncorrectOTPException(message='Incorrect OTP.')
        OTPOperations.delete_otp(email=email)
        return user_id


class UserProfileService:
    """ Class to handle user profile operations. """
    @classmethod
    def set_nickname(cls, email: str, nickname: str):
        """ Function to set a nickname for a user. """
        UserOperations.set_nickname(email=email, nickname=nickname)
