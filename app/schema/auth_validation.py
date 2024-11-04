"""
    This module contains the schema for user registration validation,
    and other authentication related validation methods
"""

from marshmallow import Schema, fields, validate


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


class LoginWithEmailValidation(Schema):
    """ Class to handle email login validation. """
    email = fields.Email(
        required=True,
        validate=validate.Length(min=1, max=75)
    )


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

class NicknameFormValidation(Schema):
    """ Class to handle nickname validation. """
    nickname = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=75)
    )
