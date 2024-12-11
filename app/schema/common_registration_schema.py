""" Common registration schema that can be used by all registration types. """

# pylint: disable=unused-argument

from marshmallow import Schema, fields, post_load, validate, validates, validates_schema
from marshmallow.exceptions import ValidationError


class EmailBaseSchema(Schema):
    """Schema for email."""
    email = fields.Email(required=True, validate=validate.Length(min=3, max=75))
    @post_load
    def normalize_email(self, in_data, **kwargs):
        """Method to convert email to lowercase."""
        in_data["email"] = in_data["email"].lower()
        return in_data

class CommonRegistrationSchema(EmailBaseSchema):
    """Schema for common registration fields.
        Consists of:
        - email
        - first_name
        - middle_name
        - last_name
        - suffix
        - phone_number
    """
    first_name = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    middle_name = fields.Str(
        required=False, missing=None, validate=validate.Length(min=0, max=50)
    )
    last_name = fields.Str(required=True, validate=validate.Length(min=3, max=100))
    suffix = fields.Str(
        required=False, missing=None, validate=validate.Length(min=0, max=10)
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
    @post_load
    def normalize_data(self, in_data, **kwargs):
        """Method to normalize the input data."""
        if "first_name" in in_data:
            in_data["first_name"] = in_data["first_name"].capitalize()
        if "middle_name" in in_data and in_data["middle_name"]:
            in_data["middle_name"] = in_data["middle_name"].capitalize()
        if "last_name" in in_data:
            in_data["last_name"] = in_data["last_name"].capitalize()
        if "suffix" in in_data and in_data["suffix"]:
            in_data["suffix"] = in_data["suffix"].capitalize()
        if "nickname" in in_data:
            in_data["nickname"] = in_data["nickname"].capitalize()
        return in_data

class ContactInfoSchema(EmailBaseSchema):
    """Schema for contact information. """
    contact_number = fields.Str(required=True, validate=validate.Regexp(r"^\+?[0-9]\d{1,14}$"))
    tax_identification_number = fields.Str(
        required=True, validate=validate.Regexp(r"^\d{3}-\d{3}-\d{3}-\d{3}$")
    )

class CoordinatesSchema(Schema):
    """Schema for coordinates."""
    longitude = fields.Float(required=True)
    latitude = fields.Float(required=True)

class LocationInfoSchema(Schema):
    """Schema for location information."""
    street_address = fields.Str(required=True)
    barangay = fields.Str(required=True)
    city = fields.Str(required=True)
    province = fields.Str(allow_none=True)
    postal_code = fields.Str(required=True, validate=validate.Regexp(r"^\d{4}$"))
    landmarks = fields.Str(allow_none=True)
    coordinates = fields.Nested(CoordinatesSchema(), required=True)

class ParkingDetailsSchema(Schema):
    """Schema for parking details."""
    space_type = fields.Str(
        required=True, validate=validate.OneOf(["indoor", "outdoor", "covered", "uncovered"])
    )
    space_layout = fields.Str(
        required=True, validate=validate.OneOf(["parallel", "perpendicular", "angled", "other"])
    )
    custom_space_layout = fields.Str(required=False)
    space_dimensions = fields.Str(
        required=True, validate=validate.Regexp(r"^\d+(\.\d+)?m x \d+(\.\d+)?m$")
    )
    access_information = fields.Str(
        required=True,
        validate=validate.OneOf(
            ["gate_code", "security_check", "key_pickup", "other", "no_special_access"]
        )
    )
    custom_access_information = fields.Str(required=True)
    is_24_7 = fields.Bool(required=False, missing=False)

    @post_load
    def normalize_data(self, in_data, **kwargs):
        """Method to normalize the input data."""
        in_data["space_type"] = in_data["space_type"].capitalize()
        in_data["space_layout"] = in_data["space_layout"].capitalize()
        in_data["access_information"] = in_data["access_information"].replace("_", " ").capitalize()
        return in_data

class FacilitiesInfoSchema(Schema):
    """Schema for facilities information."""
    lighting_and_security = fields.Str(required=True)
    accessibility = fields.Str(required=True)
    nearby_facilities = fields.Str(required=True)

class DayScheduleSchema(Schema):
    """Schema for day schedule."""
    enabled = fields.Bool(required=True)
    open = fields.Time(required=True)
    close = fields.Time(required=True)

    @validates_schema
    def validate_times(self, data, **kwargs):
        """Method to validate the times."""
        if data.get('enabled'):
            # Check if times are provided when enabled
            if not data.get('open') or not data.get('close'):
                raise ValidationError('Operating hours are required when day is enabled')

            # Check if open time is before close time
            if data['open'] >= data['close']:
                raise ValidationError('Opening time must be before closing time')

class OperatingHoursSchema(Schema):
    """Schema for operating hours."""
    monday = fields.Nested(DayScheduleSchema(), required=True)
    tuesday = fields.Nested(DayScheduleSchema(), required=True)
    wednesday = fields.Nested(DayScheduleSchema(), required=True)
    thursday = fields.Nested(DayScheduleSchema(), required=True)
    friday = fields.Nested(DayScheduleSchema(), required=True)
    saturday = fields.Nested(DayScheduleSchema(), required=True)
    sunday = fields.Nested(DayScheduleSchema(), required=True)

    @validates_schema
    def validate_has_enabled_day(self, data, **kwargs):
        """ Method to validate if at least one day is enabled. """
        if not any(day.get('enabled') for day in data.values()):
            raise ValidationError('At least one day must be enabled')

class RateSchema(Schema):
    """Schema for rate."""
    enabled = fields.Bool(required=True)
    rate = fields.Float(required=True, validate=validate.Range(min=0))
    @validates('rate')
    def validate_rate(self, value, **kwargs):
        """Method to validate the rate."""
        if self.context.get('rate_type') == 'hourly' and value > 1000:
            raise ValidationError('Hourly rate cannot exceed ₱1,000')
        if self.context.get('rate_type') == 'daily' and value > 10000:
            raise ValidationError('Daily rate cannot exceed ₱10,000')
        if self.context.get('rate_type') == 'monthly' and value > 50000:
            raise ValidationError('Monthly rate cannot exceed ₱50,000')

class PricingSchema(Schema):
    """Schema for pricing."""
    hourly = fields.Nested(RateSchema(), required=True)
    daily = fields.Nested(RateSchema(), required=True)
    monthly = fields.Nested(RateSchema(), required=True)

class PaymentMethodsSchema(Schema):
    """Schema for payment methods."""
    cash = fields.Bool(required=True)
    mobile = fields.Bool(required=True)
    other_payment = fields.Str(required=False)

class PaymentInfoSchema(Schema):
    """Schema for payment information."""
    payment_methods = fields.Nested(PaymentMethodsSchema(), required=True)
    pricing = fields.Nested(PricingSchema(), required=True)

class BasicParkingOwnerSchema(Schema):
    """Schema for individual owner."""
    first_name = fields.Str(required=False)
    last_name = fields.Str(required=False)
    middle_name = fields.Str(required=False)
    suffix = fields.Str(required=False)
    company_name = fields.Str(required=False)
    company_registration_number = fields.Str(required=False)
    owner_type = fields.Str(required=True, validate=validate.OneOf(['individual', 'company']))

    @post_load
    def normalize_data(self, in_data, **kwargs):
        """Method to normalize the input data."""
        if in_data.get('company_name'):
            in_data["company_name"] = in_data["company_name"].capitalize()
        return in_data
