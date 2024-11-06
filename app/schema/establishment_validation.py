""" Validation for new establishment data. """

from marshmallow import Schema, fields, validate


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


class UpdateEstablishmentInfoSchema(Schema):
    """Class to handle update of parking establishment information."""

    establishment_id = fields.Integer(required=True)
    manager_id = fields.Integer(required=True)
    name = fields.Str(validate=validate.Length(min=3, max=255))
    address = fields.Str(validate=validate.Length(min=3, max=255))
    contact_number = fields.Str(
        validate=[
            validate.Regexp(
                regex=r"^\+?[0-9]\d{1,14}$", error="Invalid phone number format."
            ),
            validate.Length(min=10, max=15),
        ],
    )
    opening_time = fields.Time()
    closing_time = fields.Time()
    is_24_hours = fields.Bool()
    hourly_rate = fields.Float()
    longitude = fields.Float()
    latitude = fields.Float()
