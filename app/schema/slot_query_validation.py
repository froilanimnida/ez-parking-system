""" Slot code related query validation schema. """

from marshmallow import Schema, fields, validate


class SlotCodeValidationQuerySchema(Schema):
    """Slot code validation query schema."""

    slot_code = fields.Str(required=True, validate=validate.Length(min=1, max=45))
