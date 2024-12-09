""" Common registration schema that can be used by all registration types. """

from datetime import time

from marshmallow import Schema, fields, post_load, validate, validates
from marshmallow.exceptions import ValidationError


class EmailBaseSchema(Schema):
    """Schema for email."""
    email = fields.Email(required=True, validate=validate.Length(min=3, max=75))
    @post_load
    def normalize_email(self, in_data, **kwargs):  # pylint: disable=unused-argument
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
    def normalize_data(self, in_data, **kwargs):  # pylint: disable=unused-argument
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


class DayScheduleSchema(Schema):
    """Schema for single day operating hours"""
    is_open = fields.Bool(required=True)
    opening_time = fields.Time(required=True, allow_none=True)
    closing_time = fields.Time(required=True, allow_none=True)
    @validates("opening_time")
    def validate_opening_time(self, value):
        """Validate opening time is before closing time"""
        if value and self.context.get("closing_time"):
            if value >= self.context.get("closing_time"):
                raise ValidationError("Opening time must be before closing time")


class WeeklyScheduleSchema(Schema):
    """Schema for weekly operating schedule"""
    monday = fields.Nested(DayScheduleSchema, required=True)
    tuesday = fields.Nested(DayScheduleSchema, required=True)
    wednesday = fields.Nested(DayScheduleSchema, required=True)
    thursday = fields.Nested(DayScheduleSchema, required=True)
    friday = fields.Nested(DayScheduleSchema, required=True)
    saturday = fields.Nested(DayScheduleSchema, required=True)
    sunday = fields.Nested(DayScheduleSchema, required=True)


class OperatingHoursSchema(Schema):
    """Updated schema for operating hours"""
    is_24_hours = fields.Bool(required=True)
    weekly_schedule = fields.Nested(WeeklyScheduleSchema, required=True)
    @validates("weekly_schedule")
    def validate_schedule(self, value):
        """Validate schedule based on is_24_hours"""
        if self.context.get("is_24_hours"):
            for day, schedule in value.items():  # pylint: disable=unused-variable
                if not schedule.get("is_open") or \
                   schedule.get("opening_time") != time(0,0) or \
                   schedule.get("closing_time") != time(23,59):
                    raise ValidationError(
                        "24-hour operation must have all days open with full hours"
                    )


class PricingSchema(Schema):
    """Schema for pricing information."""
    hourly_rate = fields.Float(allow_none=True, validate=validate.Range(min=0))
    daily_rate = fields.Float(allow_none=True, validate=validate.Range(min=0))
    monthly_rate = fields.Float(allow_none=True, validate=validate.Range(min=0))


class PaymentMethodsSchema(Schema):
    """Schema for payment methods."""
    cash = fields.Boolean(required=True)
    mobile = fields.Boolean(required=True)
    other = fields.Boolean(required=True)
    otherText = fields.Str(required=False, validate=validate.Length(min=3, max=255))


class ParkingEstablishmentAddressSchema(Schema):
    """ Schema for parking establishment address. """
    street_address = fields.Str(required=True)
    barangay = fields.Str(required=True)
    city = fields.Str(required=True)
    province = fields.Str(allow_none=True)
    postal_code = fields.Str(required=True, validate=validate.Regexp(r"^\d{4}$"))
    landmarks = fields.Str(allow_none=True)
    longitude = fields.Float(required=True)
    latitude = fields.Float(required=True)


class ParkingEstablishmentOtherDetailsSchema(Schema):
    """ Schema for parking establishment other details. """
    access_information = fields.Str(
        required=True,
        validate=validate.OneOf(["Gate Code", "Security Check", "Key Pickup", "No Special Access", "Other"])
    )
    access_information_custom = fields.Str(allow_none=True)
    lighting_and_security_features = fields.Str(required=True)
    accessibility_features = fields.Str(required=True)
    nearby_facilities = fields.Str(required=True)
    space_type = fields.Str(
        required=True,
        validate=validate.OneOf(["Indoor", "Outdoor", "Covered", "Uncovered"]),
    )
    space_layout = fields.Str(
        required=True, validate=validate.OneOf(["Parallel", "Perpendicular", "Angled", "Other"])
    )
    space_layout_custom = fields.Str(allow_none=True)
    space_dimensions = fields.Str(required=True, validate=validate.Regexp(r"^\d{1,3}x\d{1,3}$"))


class ParkingEstablishmentPaymentSchema(Schema):
    """ Schema for parking establishment payment. """
    payment_methods = fields.Nested(PaymentMethodsSchema(), required=True)
    pricing = fields.Nested(PricingSchema(), required=True)


class CommonParkingManagerSchema(
        ParkingEstablishmentAddressSchema, ParkingEstablishmentOtherDetailsSchema,
        ParkingEstablishmentPaymentSchema
    ):
    """ Schema for common parking manager fields. """
    owner_type = fields.Str(
        required=True, validate=validate.OneOf(["Individual", "Company"])
    )
    tax_identification_number = fields.Str(
        required=False, missing=None, validate=validate.Length(min=2, max=20)
    )
    zoning_compliance = fields.Bool(required=True)
    operating_hours = fields.Nested(OperatingHoursSchema(), required=True)
    @post_load()
    def add_role(self, in_data, **kwargs):  # pylint: disable=unused-argument
        """ Add role before processing it into database insertion """
        in_data["role"] = "parking_manager"
        return in_data
