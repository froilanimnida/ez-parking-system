""" Wraps all query related to slots and establishments, and their validations. """

from marshmallow import Schema, fields, validate


class EstablishmentQueryValidation(Schema):
    """Validation schema for slot ID."""

    establishment_id = fields.Int(required=True, validate=validate.Range(min=1))


class EstablishmentSlotTypeValidation(EstablishmentQueryValidation):
    """Validation schema for slot type."""

    vehicle_size = fields.Str(
        required=True,
        validate=validate.OneOf(["SMALL", "MEDIUM", "LARGE"]),
    )


class EstablishmentQuerySchema(Schema):
    """Validation schema for establishment query parameters."""

    longitude = fields.Float(required=False)
    latitude = fields.Float(required=False)
    establishment_id = fields.Int(required=False, validate=validate.Range(min=1))
    establishment_name = fields.Str(required=False)
    vehicle_type_id = fields.Int(required=False, validate=validate.Range(min=1))
    is_24_hours = fields.Bool(required=False)
