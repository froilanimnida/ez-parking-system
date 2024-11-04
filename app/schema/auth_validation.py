"""
    This module contains the schema for user registration validation,
    and other authentication related validation methods
"""

from marshmallow import Schema, fields, validate, pre_load



class SignUpValidation(Schema):
    """ Class to handle user registration validation. """
    first_name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100)
    )
    last_name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100)
    )
    email = fields.Email(
        required=True,
        validate=validate.Length(min=1, max=75)
    )
    phone_number = fields.Str(
        required=True,
        validate=[
            validate.Length(min=10, max=15),
            validate.Regexp(
                regex=r'^\+?[1-9]\d{1,14}$',
                error='Invalid phone number format.'
            )
        ]
    )

    @pre_load
    def normalize_email(self, **kwargs):  # pylint: disable=unused-argument
        """ Method to convert email to lowercase. """
        self.context['email'] = self.context['email'].lower()
        return self.context['email']

    @pre_load
    def normalize_first_name(self, **kwargs):  # pylint: disable=unused-argument
        """ Method to convert first name to lowercase. """
        self.context['first_name'] = self.context['first_name'].lower()
        return self.context['first_name']

    @pre_load
    def normalize_last_name(self, **kwargs):  # pylint: disable=unused-argument
        """ Method to convert last name to lowercase. """
        self.context['last_name'] = self.context['last_name'].lower()
        return self.context['last_name']


class LoginWithEmailValidation(Schema):
    """ Class to handle email login validation. """
    email = fields.Email(
        required=True,
        validate=validate.Length(min=1, max=75)
    )

    @pre_load
    def normalize_email(self, **kwargs):  # pylint: disable=unused-argument
        """ Method to convert email to lowercase. """
        self.context['email'] = self.context['email'].lower()
        return self.context['email']


class OTPGenerationSchema(Schema):
    """ Class to handle OTP validation. """
    otp = fields.Str(
        required=True,
        validate=validate.Length(min=6, max=6)
    )

class OTPSubmissionFormValidation(Schema):
    """ Class to handle OTP submission validation. """
    otp = fields.Str(
        required=True,
        validate=validate.Length(min=6, max=6)
    )
    email = fields.Email(
        required=True,
        validate=validate.Length(min=1, max=75)
    )

    @pre_load
    def normalize_email(self, **kwargs):  # pylint: disable=unused-argument
        """ Method to convert email to lowercase. """
        self.context['email'] = self.context['email'].lower()
        return self.context['email']

class NicknameFormValidation(Schema):
    """ Class to handle nickname validation. """
    nickname = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=75)
    )

    @pre_load
    def normalize_nickname(self, **kwargs):  # pylint: disable=unused-argument
        """ Method to convert nickname to lowercase. """
        self.context['nickname'] = self.context['nickname'].lower()
        return self.context['nickname']
