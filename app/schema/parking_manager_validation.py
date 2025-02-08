""" Validation for new establishment data. """

# pylint: disable=too-many-ancestors, unused-argument

from marshmallow import Schema, fields, post_load, validates_schema, validate
from marshmallow.exceptions import ValidationError

from app.schema.common_registration_schema import (
    CompanyProfile, UserData, Address, ParkingEstablishment, OperatingHour, PaymentMethod
)
from app.schema.common_schema_validation import SlotCommonValidationSchema
from app.schema.slot_validation import CreateSlotSchema


class ParkingManagerRequestSchema(Schema):
    """Validation schema for parking manager request."""
    user = fields.Nested(UserData, required=True)
    company_profile = fields.Nested(CompanyProfile, required=True)
    address = fields.Nested(Address, required=True)
    parking_establishment = fields.Nested(ParkingEstablishment, required=True)
    operating_hour = fields.Nested(
        OperatingHour, required=True
    ) # TODO: Amend this part and simplify the database to make the day of the week number based i.e 1 for monday...
    payment_method = fields.Nested(PaymentMethod, required=True)
    documents = fields.List(fields.Dict(), required=True)



class UpdateSlotSchemaSchema(SlotCommonValidationSchema, CreateSlotSchema):
    """Validation schema for update slot."""


class DeleteSlotSchemaSchema(SlotCommonValidationSchema):
    """Validation schema for delete slot."""


class ReservationValidationBaseSchema(Schema):
    """Validation schema for reservation validation."""
    transaction_code = fields.Str(required=True, validate=validate.Length(min=3))


class ValidateNewScheduleSchema(Schema):
    """Validation schema for validating new schedule."""
    opening_time = fields.Time(required=True)
    closing_time = fields.Time(required=True)
    is_24_hours = fields.Boolean(required=True)
    @validates_schema
    def validate_opening_and_closing_time(self, data, **kwargs):
        """Validate opening and closing time."""
        if data["opening_time"] >= data["closing_time"]:
            raise ValidationError("Closing time must be greater than opening time.")

    @validates_schema
    def same_closing_and_opening_time(self, data, **kwargs):
        """Validate that closing and opening time are not the same."""
        if data["opening_time"] == data["closing_time"]:
            raise ValidationError("Opening and closing time cannot be the same.")

    @post_load
    def format_time_to_24_hours_if_24_hours_establishment(self, in_data, **kwargs):
        """Format time to 24 hours if establishment is 24 hours."""
        if in_data["is_24_hours"]:
            in_data["opening_time"] = "00:00"
            in_data["closing_time"] = "23:59"
        elif in_data["opening_time"] or in_data["closing_time"]:
            # If the time is provided and the 24 hours is true flip it to false:
            in_data["is_24_hours"] = False
        return in_data


class FileUploadSchema(Schema):
    """Validation schema for file upload."""
    file = fields.Field(required=True)
