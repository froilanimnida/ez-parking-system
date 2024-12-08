""" Wraps all query related to slots and establishments, and their validations. """

from marshmallow import Schema, fields, post_load, validate

from app.utils.uuid_utility import UUIDUtility


class EstablishmentQueryValidationBase(Schema):
    """Validation schema for slot ID."""

    establishment_uuid = fields.Str(required=True)

    @post_load
    def remove_hyphen(self, data, **kwargs):  # pylint: disable=unused-argument
        """Remove hyphen from the establishment_uuid."""
        uuid_utility = UUIDUtility()
        data["establishment_uuid"] = uuid_utility.remove_hyphens_from_uuid(
            data["establishment_uuid"]
        )
        data["establishment_uuid"] = uuid_utility.uuid_to_binary(
            data["establishment_uuid"]
        )
        return data


class EstablishmentQueryValidation(EstablishmentQueryValidationBase):
    """Validation schema for establishment query parameters."""


class EstablishmentSlotTypeValidation(EstablishmentQueryValidationBase):
    """Validation schema for slot type."""

    vehicle_size = fields.Str(
        required=True,
        validate=validate.OneOf(["SMALL", "MEDIUM", "LARGE"]),
    )


class SlotCodeValidationQuerySchema(Schema):
    """Slot code validation query schema."""

    slot_uuid = fields.Str(required=True)
    
    @post_load
    def remove_hyphen(self, data, **kwargs):  # pylint: disable=unused-argument
        """Remove hyphen from the slot_uuid."""
        uuid_utility = UUIDUtility()
        data["slot_uuid"] = uuid_utility.remove_hyphens_from_uuid(
            data["slot_uuid"]
        )
        data["slot_uuid"] = uuid_utility.uuid_to_binary(
            data["slot_uuid"]
        )
        return data


class EstablishmentQuerySchema(Schema):
    """Validation schema for establishment query parameters."""

    longitude = fields.Float(required=False)
    latitude = fields.Float(required=False)
    establishment_name = fields.Str(required=False)
    vehicle_type_id = fields.Int(required=False, validate=validate.Range(min=1))
    is_24_hours = fields.Bool(required=False)
