"""
    This module contains the schema for user registration validation,
    and other authentication related validation methods
"""

from marshmallow import Schema, fields, validate, post_load


class SignUpValidationSchema(Schema):
    """Class to handle user registration validation."""

    first_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    last_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(
        required=True,
        validate=[
            validate.Length(min=1, max=75),
            validate.Email(error="Invalid email format."),
        ],
    )
    phone_number = fields.Str(
        required=True,
        validate=[
            validate.Length(min=10, max=15),
            validate.Regexp(
                regex=r"^\+?[1-9]\d{1,14}$", error="Invalid phone number format."
            ),
        ],
    )
    role = fields.Str(
        required=True,
        validate=validate.OneOf(["user", "parking_manager", "admin"]),
    )

    @post_load
    def normalize_email(self, in_data, **kwargs):  # pylint: disable=unused-argument
        """Method to convert email to lowercase."""
        in_data["email"] = in_data["email"].lower()
        return in_data

    @post_load
    def normalize_first_name(
        self, in_data, **kwargs
    ):  # pylint: disable=unused-argument
        """Method to convert first name to lowercase."""
        in_data["first_name"] = in_data["first_name"].capitalize()
        return in_data

    @post_load
    def normalize_last_name(self, in_data, **kwargs):  # pylint: disable=unused-argument
        """Method to convert last name to lowercase."""
        in_data["last_name"] = in_data["last_name"].capitalize()
        return in_data


class LoginWithEmailValidationSchema(Schema):
    """Class to handle email login validation."""

    email = fields.Email(required=True, validate=validate.Length(min=1, max=75))

    @post_load
    def normalize_email(self, in_data, **kwargs):  # pylint: disable=unused-argument
        """Method to convert email to lowercase."""
        in_data["email"] = in_data["email"].lower()
        return in_data


class OTPGenerationSchema(Schema):
    """Class to handle OTP validation."""

    otp = fields.Str(required=True, validate=validate.Length(min=6, max=6))


class OTPSubmissionSchema(Schema):
    """Class to handle OTP submission validation."""

    otp = fields.Str(required=True, validate=validate.Length(min=6, max=6))
    email = fields.Email(required=True, validate=validate.Length(min=1, max=75))

    @post_load
    def normalize_email(self, in_data, **kwargs):  # pylint: disable=unused-argument
        """Method to convert email to lowercase."""
        in_data["email"] = in_data["email"].lower()
        return in_data


class NicknameFormValidationSchema(Schema):
    """Class to handle nickname validation."""

    nickname = fields.Str(required=True, validate=validate.Length(min=1, max=75))

    @post_load
    def normalize_nickname(self, in_data, **kwargs):  # pylint: disable=unused-argument
        """Method to convert nickname to lowercase."""
        in_data["nickname"] = in_data["nickname"].lower()
        return in_data
