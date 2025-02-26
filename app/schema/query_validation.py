""" Wraps all query related to slots and establishments, and their validations. """

from marshmallow import Schema, fields, validate

from app.schema.common_schema_validation import (
    EstablishmentCommonValidationSchema, SlotCommonValidationSchema
)

class EstablishmentQueryValidationSchema(EstablishmentCommonValidationSchema):
    """Validation schema for establishment query parameters."""


class EstablishmentSlotTypeValidationSchema(EstablishmentCommonValidationSchema):
    """Validation schema for slot type."""

    vehicle_size = fields.Str(
        required=True,
        validate=validate.OneOf(["SMALL", "MEDIUM", "LARGE"]),
    )


class SlotCodeValidationSchemaQuerySchema(SlotCommonValidationSchema):
    """Slot code validation query schema."""


class EstablishmentQuerySchema(Schema):
    """Validation schema for establishment query parameters."""
    user_longitude = fields.Float(required=False)
    user_latitude = fields.Float(required=False)
    city = fields.Str(required=False)
    search_term = fields.Str(required=False)
