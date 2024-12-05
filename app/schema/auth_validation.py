"""
    This module contains the schema for user registration validation,
    and other authentication related validation methods
"""

from marshmallow import (
    Schema,
    ValidationError,
    fields,
    validate,
    post_load,
    validates_schema,
)


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


class IndividualOwnerSchema(Schema):
    """Schema for individual owner details."""

    first_name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    middle_name = fields.Str(allow_none=True)
    last_name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    suffix = fields.Str(allow_none=True)


class CompanyOwnerSchema(Schema):
    """Schema for company owner details."""

    business_name = fields.Str(required=True, validate=validate.Length(min=2, max=255))
    company_reg_number = fields.Str(required=True)


class OperatingHoursSchema(Schema):
    """Schema for operating hours."""

    open_time = fields.Time(required=True)
    close_time = fields.Time(required=True)
    is_open = fields.Bool(required=True)


class PricingSchema(Schema):
    """Schema for pricing information."""

    hourly_rate = fields.Float(allow_none=True, validate=validate.Range(min=0))
    daily_rate = fields.Float(allow_none=True, validate=validate.Range(min=0))
    monthly_rate = fields.Float(allow_none=True, validate=validate.Range(min=0))


class ParkingManagerAccountCreationSchema(Schema):
    """Class to handle parking manager account creation validation."""

    owner_type = fields.Str(
        required=True, validate=validate.OneOf(["Individual", "Company"])
    )
    individual_details = fields.Nested(IndividualOwnerSchema, required=False)
    company_details = fields.Nested(CompanyOwnerSchema, required=False)

    contact_number = fields.Str(
        required=True, validate=validate.Regexp(r"^\+?[0-9]{10,15}$")
    )
    email = fields.Email(required=True)
    tin = fields.Str(required=True, validate=validate.Regexp(r"^\d{9,12}$"))

    # Location details
    street_address = fields.Str(required=True)
    barangay = fields.Str(required=True)
    city = fields.Str(required=True)
    province = fields.Str(allow_none=True)
    postal_code = fields.Str(required=True, validate=validate.Regexp(r"^\d{4}$"))
    landmarks = fields.Str(allow_none=True)

    space_type = fields.Str(
        required=True,
        validate=validate.OneOf(["Indoor", "Outdoor", "Covered", "Uncovered"]),
    )
    space_layout = fields.Str(required=True)
    space_dimensions = fields.Str(required=True)

    # Operating hours for each day
    operating_hours = fields.Dict(
        keys=fields.Str(), values=fields.Nested(OperatingHoursSchema), required=True
    )

    # Facilities
    lighting_security = fields.Str(required=True)
    accessibility_options = fields.Str(required=True)
    nearby_facilities = fields.Str(required=True)

    # Pricing
    pricing = fields.Nested(PricingSchema, required=True)
    payment_methods = fields.List(fields.Str(), required=True)

    # Legal compliance
    zoning_compliance = fields.Bool(required=True)

    @validates_schema
    def validate_owner_details(self, data, **kwargs):  # pylint: disable=unused-argument
        """Validate that appropriate owner details are provided."""
        if data["owner_type"] == "Individual" and not data.get("individual_details"):
            raise ValidationError(
                "Individual details required for individual owner type"
            )
        if data["owner_type"] == "Company" and not data.get("company_details"):
            raise ValidationError("Company details required for company owner type")

    @validates_schema
    def validate_pricing(self, data, **kwargs):
        """Validate that at least one pricing option is provided."""
        pricing = data.get("pricing", {})
        if not any(
            [
                pricing.get("hourly_rate"),
                pricing.get("daily_rate"),
                pricing.get("monthly_rate"),
            ]
        ):
            raise ValidationError("At least one pricing rate must be provided")
