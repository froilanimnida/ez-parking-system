""" Validation for new establishment data. """

# pylint: disable=too-many-ancestors, unused-argument

from marshmallow import Schema, fields, post_load, validates_schema, validate
from marshmallow.exceptions import ValidationError

from app.schema.common_schema_validation import SlotCommonValidation
from app.schema.slot_validation import CreateSlotSchema
from app.schema.common_registration_schema import (
    ContactInfoSchema, LocationInfoSchema, ParkingDetailsSchema, FacilitiesInfoSchema,
    OperatingHoursSchema, PaymentInfoSchema, BasicParkingOwnerSchema
)


class ParkingManagerRequestSchema(Schema):
    """Validation schema for parking manager request."""
    owner_info = fields.Nested(BasicParkingOwnerSchema, required=True)
    contact_info = fields.Nested(ContactInfoSchema, required=True)
    location_info = fields.Nested(LocationInfoSchema, required=True)
    parking_details = fields.Nested(ParkingDetailsSchema, required=True)
    facilities_info = fields.Nested(FacilitiesInfoSchema, required=True)
    operating_hours = fields.Nested(OperatingHoursSchema, required=True)
    payment_info = fields.Nested(PaymentInfoSchema, required=True)
    documents = fields.List(fields.Dict(), required=True)

    @post_load()
    def add_role(self, in_data, **kwargs):  # pylint: disable=unused-argument
        """Method to add role to the user."""
        in_data["role"] = "user"
        return in_data


class UpdateSlotSchema(SlotCommonValidation, CreateSlotSchema):
    """Validation schema for update slot."""


class DeleteSlotSchema(SlotCommonValidation):
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
