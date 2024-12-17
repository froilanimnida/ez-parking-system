""" Wraps all query related to slots and establishments, and their validations. """

from marshmallow import Schema, fields, validate

from app.schema.common_schema_validation import EstablishmentCommonValidation, SlotCommonValidation


class EstablishmentQueryValidation(EstablishmentCommonValidation):
    """Validation schema for establishment query parameters."""


class EstablishmentSlotTypeValidation(EstablishmentCommonValidation):
    """Validation schema for slot type."""

    vehicle_size = fields.Str(
        required=True,
        validate=validate.OneOf(["SMALL", "MEDIUM", "LARGE"]),
    )


class SlotCodeValidationQuerySchema(SlotCommonValidation):
    """Slot code validation query schema."""


class EstablishmentQuerySchema(Schema):
    """Validation schema for establishment query parameters."""
    user_longitude = fields.Float(required=False)
    user_latitude = fields.Float(required=False)
    establishment_name = fields.Str(required=False)
