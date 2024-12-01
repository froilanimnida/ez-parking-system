""" Incoming transaction related validation schema. """

from marshmallow import Schema, fields, validate, post_load

from app.utils.uuid_utility import UUIDUtility


class TransactionBaseValidationSchema(Schema):
    """Base schema for the transaction validation."""

    transaction_uuid = fields.Str(required=True)

    @post_load
    def remove_hyphen(self, data, **kwargs):  # pylint: disable=unused-argument
        """Remove hyphen from the UUID."""
        uuid_utility = UUIDUtility()
        data["transaction_uuid"] = uuid_utility.remove_hyphens_from_uuid(
            data["transaction_uuid"]
        )
        data["transaction_uuid"] = uuid_utility.uuid_to_binary(data["transaction_uuid"])
        return data


class CancelReservationSchema(TransactionBaseValidationSchema):
    """Schema for the reservation cancellation."""


class ViewTransactionSchema(TransactionBaseValidationSchema):
    """Schema for the transaction view."""


class ReservationCreationSchema(Schema):
    """Schema for the reservation creation."""

    establishment_uuid = fields.Str(required=True)
    slot_id = fields.Integer(required=True, validate=validate.Range(min=1))
    vehicle_type_id = fields.Integer(required=True, validate=validate.Range(min=1))
    @post_load
    def remove_hyphen(self, data, **kwargs):  # pylint: disable=unused-argument
        """Remove hyphen from the UUID."""
        uuid_utility = UUIDUtility()
        data["establishment_uuid"] = uuid_utility.remove_hyphens_from_uuid(
            data["establishment_uuid"]
        )
        data["establishment_uuid"] = uuid_utility.uuid_to_binary(data["establishment_uuid"])
        return data


class TransactionFormDetailsSchema(Schema):
    """Schema for the transaction form details."""
    establishment_uuid = fields.Str(required=True)
    slot_code = fields.Str(required=True)
    @post_load
    def remove_hyphen(self, data, **kwargs):  # pylint: disable=unused-argument
        """Remove hyphen from the UUID."""
        uuid_utility = UUIDUtility()
        data["establishment_uuid"] = uuid_utility.remove_hyphens_from_uuid(
            data["establishment_uuid"]
        )
        data["establishment_uuid"] = uuid_utility.uuid_to_binary(data["establishment_uuid"])
        return data
