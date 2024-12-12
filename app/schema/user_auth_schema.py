""" User Authentication Schema. """

from marshmallow import fields, validate, Schema, post_load

from app.schema.common_registration_schema import UserSchema, EmailBaseSchema

class UserBaseSchema(UserSchema):
    """Schema for user registration."""
    nickname = fields.Str(required=True, validate=validate.Length(min=3, max=24))
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
    def normalize_data(
        self, in_data, **kwargs
    ):  # pylint: disable=unused-argument
        """Method to normalize the input data."""
        if "plate_number" in in_data:
            in_data["plate_number"] = in_data["plate_number"].upper().replace(" ", "")
        if "nickname" in in_data:
            in_data["nickname"] = in_data["nickname"].capitalize()
        return in_data
    @post_load()
    def add_role(self, in_data, **kwargs):  # pylint: disable=unused-argument
        """Method to add role to the user."""
        in_data["role"] = "user"
        return in_data

class UserRegistrationSchema(Schema):
    """Schema for user registration."""
    user = fields.Nested(UserBaseSchema, required=True)



class UserLoginSchema(EmailBaseSchema):
    """Schema for user login."""
    role = fields.Str(
        required=True, validate=validate.OneOf(["user", "admin", "parking_manager"])
    )


class OTPLoginBaseSchema(EmailBaseSchema):
    """Schema for OTP login."""
    otp = fields.Str(required=True, validate=validate.Length(equal=6))
    remember_me = fields.Bool(required=False, missing=False)


class GenerateOTPBaseSchema(EmailBaseSchema):
    """Schema for generating OTP."""


class OTPLoginSchema(OTPLoginBaseSchema):
    """Schema for OTP login."""


class EmailVerificationSchema(Schema):
    """Class to handle email verification validation."""
    verification_token = fields.Str(required=True, validate=validate.Length(min=1, max=200))
