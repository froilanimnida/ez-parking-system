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


class LoginWithEmail(Schema):
    """ Class to handle email login validation. """
    email = fields.Email(
        required=True,
        validate=validate.Length(min=1, max=75)
    )
