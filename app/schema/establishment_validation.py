""" Validation for new establishment data. """

from marshmallow import Schema, fields, post_load, validate, validates_schema
from marshmallow.exceptions import ValidationError


class EstablishmentValidationSchema(Schema):
    """Class to handle parking establishment validation."""

    manager_id = fields.Integer(required=True)
    name = fields.Str(required=True, validate=validate.Length(min=3, max=255))
    address = fields.Str(required=True, validate=validate.Length(min=3, max=255))
    contact_number = fields.Str(
        required=True,
        validate=[
            validate.Regexp(
                regex=r"^\+?[0-9]\d{1,14}$", error="Invalid phone number format."
            ),
            validate.Length(min=10, max=15),
        ],
    )
    opening_time = fields.Time(required=True)
    closing_time = fields.Time(required=True)
    is_24_hours = fields.Bool(required=True)
    hourly_rate = fields.Float(required=True)
    longitude = fields.Float(required=True)
    latitude = fields.Float(required=True)

    @validates_schema
    def validate_opening_and_closing_time(
        self, data, **kwargs  # pylint: disable=unused-argument
    ):
        """Validate opening and closing time."""
        if data["opening_time"] >= data["closing_time"]:
            raise ValidationError("Closing time must be greater than opening time.")

    @validates_schema
    def same_closing_and_opening_time(
        self, data, **kwargs  # pylint: disable=unused-argument
    ):
        """Validate that closing and opening time are not the same."""
        if data["opening_time"] == data["closing_time"]:
            raise ValidationError("Opening and closing time cannot be the same.")

    @post_load
    def format_time_to_24_hours_if_24_hours_establishment(
        self, in_data, **kwargs  # pylint: disable=unused-argument
    ):
        """Format time to 24 hours if establishment is 24 hours."""

        if in_data["is_24_hours"]:
            in_data["opening_time"] = "00:00"
            in_data["closing_time"] = "23:59"
        elif in_data["opening_time"] or in_data["closing_time"]:
            # If the time is provided and the 24 hours is true flip it to false:
            in_data["is_24_hours"] = False
        return in_data


class UpdateEstablishmentInfoSchema(Schema):
    """Class to handle update of parking establishment information."""

    establishment_id = fields.Integer(required=True)
    manager_id = fields.Integer(required=True)
    name = fields.Str(required=True, validate=validate.Length(min=3, max=255))
    address = fields.Str(required=True, validate=validate.Length(min=3, max=255))
    contact_number = fields.Str(
        required=True,
        validate=[
            validate.Regexp(
                regex=r"^\+?[0-9]\d{1,14}$", error="Invalid phone number format."
            ),
            validate.Length(min=10, max=15),
        ],
    )
    opening_time = fields.Time(required=True)
    closing_time = fields.Time(required=True)
    is_24_hours = fields.Bool(required=True)
    hourly_rate = fields.Float(required=True)
    longitude = fields.Float(required=True)
    latitude = fields.Float(required=True)

    @post_load
    def format_time_to_24_hours_if_24_hours_establishment(
        self, in_data, **kwargs  # pylint: disable=unused-argument
    ):
        """Format time to 24 hours if establishment is 24 hours."""

        if in_data["opening_time"] or in_data["closing_time"]:
            # If the time is provided and the 24 hours is true flip it to false:
            in_data["is_24_hours"] = False
        elif in_data["is_24_hours"]:
            in_data["opening_time"] = "00:00:00:00:00"
            in_data["closing_time"] = "23:59:59:59:59"
        return in_data

    @validates_schema
    def validate_opening_and_closing_time(
        self, data, **kwargs  # pylint: disable=unused-argument
    ):
        """Validate opening and closing time."""
        if data["opening_time"] >= data["closing_time"]:
            raise ValidationError("Closing time must be greater than opening time.")
