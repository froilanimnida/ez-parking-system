""" Slot code related query validation schema. """

from marshmallow import Schema, fields, validate


class SlotCodeValidationQuerySchema(Schema):
    """Slot code validation query schema."""
    slot_code = fields.Str(required=True, validate=validate.Length(min=1, max=45))



class CreateSlotSchema(SlotCodeValidationQuerySchema):
    """Validation schema for create slot."""
    establishment_uuid = fields.Str(required=True, validate=validate.Length(min=3, max=45))
    vehicle_type_id = fields.Integer(required=True)
    slot_status = fields.Str(
        required=False,
        validate=validate.OneOf(['open', 'occupied', 'reserved', 'closed']),
    )
    is_active = fields.Boolean(required=False, missing=True)
    slot_multiplier = fields.Decimal(
        required=True, validate=validate.Range(min=0, max=999999)
    )
    floor_level = fields.Integer(required=True, validate=validate.Range(min=0, max=99))
    base_rate = fields.Decimal(required=True, validate=validate.Range(min=0, max=999999))
    is_premium = fields.Boolean(required=True)
    slot_features = fields.Str(required=False, missing="standard", validate=validate.OneOf(
        ['standard', 'covered', "vip", "disabled", "ev_charging"]
    ))
