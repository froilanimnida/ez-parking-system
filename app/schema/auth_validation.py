"""
    This module contains the schema for user registration validation,
    and other authentication related validation methods
"""

from marshmallow import Schema, fields, validate, post_load


# noinspection PyUnusedLocal
class SignUpValidationSchema(Schema):
    """Class to handle user registration validation."""

    first_name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    last_name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
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
                regex=r"^\+?[0-9]\d{1,14}$", error="Invalid phone number format."
            ),
        ],
    )
    role = fields.Str(
        required=True,
        validate=validate.OneOf(["User", "Parking Manager", "Admin"]),
    )
    nickname = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=24),
    )
    plate_number = fields.Str(
        required=True,
        validate=[
            validate.Length(min=6, max=8),
            validate.Regexp(
                regex=r"^(?:"
                r"[A-Z]{2,3}[\s-]?\d{3,4}|"
                r"CD[\s-]?\d{4}|"
                r"[A-Z]{3}[\s-]?\d{3}|"
                r"\d{4}"
                r")$",
                error=(
                    "Invalid plate number format. Please use one of these formats:\n"
                    "• Private vehicles: ABC 123 or ABC 1234\n"
                    "• Diplomatic: CD 1234\n"
                    "• Government: SFP 123\n"
                    "• Special: 1234"
                ),
            ),
        ],
    )

    @post_load
    def normalize_plate_number(
        self, in_data, **kwargs
    ):  # pylint: disable=unused-argument
        """Normalize plate number format by removing spaces and converting to uppercase"""
        if "plate_number" in in_data:
            in_data["plate_number"] = in_data["plate_number"].upper().replace(" ", "")
        return in_data

    @post_load
    def normalize_email(self, in_data, **kwargs):  # pylint: disable=unused-argument
        """Method to convert email to lowercase."""
        in_data["email"] = in_data["email"].lower()
        return in_data

    @post_load
    def normalize_first_name(
        self, in_data, **kwargs  # pylint: disable=unused-argument
    ):
        """Method to convert first name to lowercase."""
        in_data["first_name"] = in_data["first_name"].capitalize()
        return in_data

    @post_load
    def normalize_last_name(self, in_data, **kwargs):  # pylint: disable=unused-argument
        """Method to convert last name to lowercase."""
        in_data["last_name"] = in_data["last_name"].capitalize()
        return in_data

    @post_load
    def normalize_role(self, in_data, **kwargs):  # pylint: disable=unused-argument
        """Method to convert role to lowercase."""
        in_data["role"] = in_data["role"].lower().replace(" ", "_")
        return in_data


# noinspection PyUnusedLocal
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
    remember_me = fields.Bool(required=False)

    @post_load
    def normalize_email(self, in_data, **kwargs):  # pylint: disable=unused-argument
        """Method to convert email to lowercase."""
        in_data["email"] = in_data["email"].lower()
        return in_data


class EmailVerificationSchema(Schema):
    """Class to handle email verification validation."""

    verification_token = fields.Str(
        required=True, validate=validate.Length(min=1, max=200)
    )
