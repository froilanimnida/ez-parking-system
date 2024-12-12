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

class UserSchema(EmailBaseSchema):
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


class UserData(UserSchema):
    """Schema for individual owner."""
    first_name = fields.Str(required=False, validate=validate.Length(min=3, max=50))
    last_name = fields.Str(required=False, validate=validate.Length(min=3, max=100))
    middle_name = fields.Str(required=False)
    suffix = fields.Str(required=False)

    @post_load()
    def add_role(self, in_data, **kwargs):  # pylint: disable=unused-argument
        """Method to add role to the user."""
        in_data["role"] = "parking_manager"
        return in_data

class CompanyProfile(Schema):
    """Schema for company profile."""
    owner_type = fields.Str(required=True, validate=validate.OneOf(['individual', 'company']))
    company_name = fields.Str(required=False)
    company_reg_number = fields.Str(required=False)
    tin = fields.Str(
        required=False, validate=validate.Regexp(r"^\d{3}-\d{3}-\d{3}-\d{3}$")
    )

    @post_load
    def normalize_data(self, in_data, **kwargs):
        """Method to normalize the input data."""
        if in_data.get('company_name'):
            in_data["company_name"] = in_data["company_name"].capitalize()
        return in_data


class Address(Schema):
    """Schema for address."""
    street = fields.Str(required=True)
    barangay = fields.Str(required=True)
    city = fields.Str(required=True)
    province = fields.Str(required=False)
    postal_code = fields.Str(required=True, validate=validate.Regexp(r"^\d{4}$"))


class ParkingEstablishment(Schema):
    """Schema for parking establishment."""
    space_type = fields.Str(
        required=True, validate=validate.OneOf(["indoor", "outdoor", "covered", "uncovered"])
    )
    space_layout = fields.Str(
        required=True, validate=validate.OneOf(["parallel", "perpendicular", "angled", "other"])
    )
    custom_layout = fields.Str(required=False)
    dimensions = fields.Str(
        required=True, validate=validate.Regexp(r".*\d.*")
    )
    is24_7 = fields.Bool(required=False, missing=False)
    access_info = fields.Str(
        required=False,
        validate=validate.OneOf(
            ["gate_code", "security_check", "key_pickup", "other", "no_special_access"]
        )
    )
    custom_access = fields.Str(required=False)
    status = fields.Str(required=False, missing="pending")
    name = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    lighting = fields.Str(required=True)
    accessibility = fields.Str(required=True)
    facilities = fields.Str(required=True)
    nearby_landmarks = fields.Str(required=False)
    longitude = fields.Float(required=True, validate=validate.Range(min=-180, max=180))
    latitude = fields.Float(required=True, validate=validate.Range(min=-90, max=90))


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

class OperatingHour(Schema):
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


class PaymentMethod(Schema):
    """Schema for payment method."""
    accepts_cash = fields.Bool(required=True)
    accepts_mobile = fields.Bool(required=True)
    accepts_other = fields.Bool(required=False)
    other_methods = fields.Str(required=False)


class RateSchema(Schema):
    """Schema for rate."""
    rate_type = fields.Str(required=True, validate=validate.OneOf(['hourly', 'daily', 'monthly']))
    is_enabled = fields.Bool(required=True)
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


class PricingPlan(Schema):
    """Schema for pricing plan."""
    hourly = fields.Nested(RateSchema, required=False, context={'rate_type': 'hourly'})
    daily = fields.Nested(RateSchema, required=False, context={'rate_type': 'daily'})
    monthly = fields.Nested(RateSchema, required=False, context={'rate_type': 'monthly'})

    @validates_schema
    def validate_at_least_one_rate(self, data, **kwargs):
        """Validate that at least one rate type is enabled."""
        enabled_rates = [
            rate['is_enabled']
            for rate in [
                data.get('hourly', {}),
                data.get('daily', {}),
                data.get('monthly', {})
            ]
            if rate
        ]

        if not any(enabled_rates):
            raise ValidationError('At least one rate type must be enabled')
