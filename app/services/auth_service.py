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
from bcrypt import hashpw, gensalt, checkpw
from flask_jwt_extended import create_access_token
from pyotp import TOTP

from app.exceptions.authorization_exception import (EmailAlreadyTaken, ExpiredOTPException, IncorrectOTPException, MissingFieldsException,
                                                    InvalidEmailException, InvalidPhoneNumberException,
                                                    PasswordTooShort, IncorrectPasswordException,
                                                    EmailNotFoundException)
from app.models.user import UserOperations, OTPOperations
from app.utils.email_utility import send_mail


class AuthService:
    """ Class to handle user authentication operations. """
    @classmethod
    def create_new_user(cls, registration_data: dict) -> str:  # pylint: disable=C0116
        return UserRegistrationService.register_user(user_data=registration_data)

    @classmethod
    def login_user(cls, login_data: dict) -> str:  # pylint: disable=C0116
        return UserLoginService.login_user(login_data=login_data)

    @classmethod
    def generate_otp(cls, user_data: dict) -> str:  # pylint: disable=C0116
        return UserOTPService.generate_otp(user_id=user_data.get('user_id'))

    @classmethod
    def verify_otp(cls, user_data: dict) -> str:  # pylint: disable=C0116
        return UserOTPService.verify_otp(otp=user_data.get('otp'), email=user_data.get('email'))


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
        plain_text_password = user_data.get('password')
        if len(str(object=plain_text_password)) < 8 or not plain_text_password:
            raise PasswordTooShort('Password must be at least 8 characters')

        salt: str = gensalt(rounds=16).decode(encoding='utf=8')
        username: str = str(object=user_data
                            .get('email')).split(sep='@', maxsplit=1)[0]
        first_name = user_data.get('first_name')
        last_name = user_data.get('last_name')
        role = 'user'
        uuid: bytes = uuid4().bytes
        if not first_name or not last_name:
            raise MissingFieldsException(
                message='Please provide all the required fields.')
        hashed_password: str = hashpw(password=plain_text_password.encode(
            'utf-8'), salt=salt.encode(encoding='utf-8')).decode(encoding='utf-8')
        user_data = {
            'uuid': uuid,
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'phone_number': phone_number,
            'salt': salt,
            'hashed_password': hashed_password,
            'role': role
        }
        return UserOperations.create_new_user(user_data=user_data)


class UserLoginService:
    """ Class to handle user login operations. """
    @classmethod
    def login_user(cls, login_data: dict) -> str:  # pylint: disable=C0116
        email = login_data.get('email')
        plaintext_password = login_data.get('password')
        if not email or not plaintext_password:
            raise MissingFieldsException(
                message='Please provide an email address.')

        is_email_taken = UserOperations.is_email_taken(email=email)
        if not is_email_taken:
            raise EmailNotFoundException(message='Email not found.')

        if not re.search(pattern=r'^[a-z0-9]+[._]?[a-z0-9]+@\w+[.]\w+$', string=email):
            raise InvalidEmailException(
                'Please provide a valid email address.')
        user = UserOperations.login_user(email=email)
        user_id, user_first_name, user_last_name, user_email, hashed_password = user
        is_password_matched = checkpw(
            password=plaintext_password.encode('utf-8'), hashed_password=hashed_password.encode('utf-8'))
        if not is_password_matched:
            raise IncorrectPasswordException(message='Incorrect password.')
        # Send otp to user to their email by calling the generate_otp method
        return (UserOTPService
                .generate_otp(user_id=user_id, email=user_email, first_name=user_first_name, last_name=user_last_name))


class SessionTokenService:  # pylint: disable=R0903
    """ This class is responsible for the session token service. """
    @staticmethod
    def generate_session_token(email) -> str:
        """This is the function responsible for generating the session token."""
        return create_access_token(identity={'email': email})


class UserOTPService:
    """ Class to handle user OTP operations. """
    @classmethod
    def generate_otp(cls, user_id: str, email: str, first_name: str, last_name: str) -> str:
        """ Function to generate an OTP for a user. """
        seed = f"{getenv('TOTP_SECRET_KEY')}{int(time.time())}"
        user_full_name = f'{first_name} {last_name}'
        six_digits_otp = TOTP(base64.b32encode(bytes.fromhex(seed))
                              .decode('UTF-8'),
                              digits=6, interval=300, digest=sha256).now()
        otp_expiry: datetime = datetime.now() + timedelta(minutes=5)
        one_time_password_template = render_template('auth/one-time-password.html',
                                                     otp=six_digits_otp, user_name=user_full_name)
        data: dict[str, str | datetime] = {
            'user_id': int(user_id),
            'otp_secret': six_digits_otp,
            'otp_expiry': otp_expiry
        }
        OTPOperations.set_otp(data=data)
        send_mail(message=one_time_password_template, email=email, subject="One Time Password")
        return 'success'

    @classmethod
    def verify_otp(cls, otp: str, email: str):  # pylint: disable=W0613
        """ Function to verify an OTP for a user. """
        retrieved_otp, expiry = OTPOperations.get_otp(email=email)
        if datetime.now() > expiry:
            raise ExpiredOTPException(message='OTP has expired.')
        if retrieved_otp != otp or not otp:
            raise IncorrectOTPException(message='Incorrect OTP.')
        OTPOperations.delete_otp(email=email)
        return SessionTokenService.generate_session_token(email=email)
        
