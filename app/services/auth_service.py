
from bcrypt import hashpw, gensalt, checkpw
from re import search, compile
from uuid import uuid4
from flask_jwt_extended import create_access_token
from app.exceptions.authorization_exception import (EmailAlreadyTaken, MissingFieldsException,
                                                    InvalidEmailException, InvalidPhoneNumberException,
                                                    PasswordTooShort, IncorrectPasswordException,
                                                    EmailNotFoundException)
from app.models.user import UserOperations


class AuthService:
    @classmethod
    def create_new_user(cls, registration_data: dict):  # pylint: disable=C0116
        return UserRegistrationService.register_user(registration_data)
    
    @classmethod
    def login_user(cls, login_data: dict):  # pylint: disable=C0116
        return UserLoginService.login_user(login_data)
    

class UserRegistrationService:
    """ Class to handle user registration operations. """
    @classmethod
    def register_user(cls, user_data: dict):
        email = user_data.get('email')
        if not email:
            raise MissingFieldsException('Please provide an email address.')
        
        if not search(r'^[a-z0-9]+[._]?[a-z0-9]+@\w+[.]\w+$', email):
            raise InvalidEmailException('Please provide a valid email address.')
        
        is_email_taken = UserOperations.is_email_taken(user_data.get('email'))
        if is_email_taken:
            raise EmailAlreadyTaken('Email already taken.')
        
        phone_number = user_data.get('phone_number')
        phone_number_regex = compile(r'^\+?1?\d{9,15}$')
        if not phone_number_regex.match(phone_number):
            raise InvalidPhoneNumberException('Please provide a valid phone number.')
        
        plain_text_password = user_data.get('password')
        if len(str(plain_text_password)) < 8 or not plain_text_password:
            raise PasswordTooShort('Password must be at least 8 characters')
        
        salt = gensalt(rounds=16).decode('utf=8')
        username = str(user_data.get('email')).split('@')[0]
        first_name = user_data.get('first_name')
        last_name = user_data.get('last_name')
        role = 'user'
        uuid = uuid4().bytes
        if not first_name or not last_name:
            raise MissingFieldsException('Please provide all the required fields.')
        hashed_password = hashpw(user_data.get('password').encode(
                'utf-8'), salt.encode('utf-8')).decode('utf-8')
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
        return UserOperations.create_new_user(user_data)

class UserLoginService:
    """ Class to handle user login operations. """
    @classmethod
    def login_user(cls, login_data: dict):
        email = login_data.get('email')
        if not email:
            raise MissingFieldsException('Please provide an email address.')
        
        is_email_taken = UserOperations.is_email_taken(email)
        if not is_email_taken:
            raise EmailNotFoundException('Email not found.')
        
        if not search(r'^[a-z0-9]+[._]?[a-z0-9]+@\w+[.]\w+$', email):
            raise InvalidEmailException('Please provide a valid email address.')
        plaintext_password = login_data.get('password')
        if not plaintext_password:
            raise MissingFieldsException('Please provide a password.')
        if len(str(plaintext_password)):
            raise PasswordTooShort('Password must be at least 8 characters long.')
        user = UserOperations.login_user(login_data)
        user_id, user_email, hashed_password, salt = user.get('id'), user.get('email'), user.get('hashed_password'), user.get('salt')
        if not checkpw(plaintext_password.encode('utf-8'), hashed_password.encode('utf-8')):
            raise IncorrectPasswordException('Incorrect password.')
        session_token = SessionTokenService.generate_session_token(email, user_id)
        return session_token


class SessionTokenService:  # pylint: disable=R0903
    """ This class is responsible for the session token service. """
    @staticmethod
    def generate_session_token(email, user_id):
        """This is the function responsible for generating the session token."""
        return create_access_token(identity={'email': email, 'user_id': user_id})
    
