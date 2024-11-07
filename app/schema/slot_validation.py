"""Marshmallow schema for validating parking slot data.

    Defines required fields and validation rules for creating/updating a parking slot:
    - establishment_id: ID of the establishment the slot belongs to
    - slot_code: Unique identifier code for the slot (3-45 chars)
    - vehicle_type_id: ID of the allowed vehicle type
    - slot_status: Current status (open/reserved/occupied)
    - is_active: Whether the slot is active in the system
"""

from marshmallow import Schema, fields, validate


class SlotValidationSchema(Schema):  # pylint: disable=C0115
    establishment_id = fields.Integer(required=True)
    slot_code = fields.Str(required=True, validate=validate.Length(min=3, max=45))
    vehicle_type_id = fields.Integer(required=True)
    slot_status = fields.Str(
        required=True, validate=validate.OneOf(["open", "reserved", "occupied"])
    )
    is_active = fields.Boolean(required=True)
