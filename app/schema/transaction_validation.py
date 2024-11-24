""" Incoming transaction related validation schema. """

from marshmallow import Schema, fields, validate, post_load


class TransactionBaseValidationSchema(Schema):
    """Base schema for the transaction validation."""

    transaction_uuid = fields.Str(required=True)

    @post_load
    def remove_hyphen(self, data, **kwargs):  # pylint: disable=unused-argument
        """Remove hyphen from the UUID."""
        data["transaction_uuid"] = data["transaction_uuid"].replace("-", "")
        return data


class CancelReservationSchema(TransactionBaseValidationSchema):
    """Schema for the reservation cancellation."""


class ViewTransactionSchema(TransactionBaseValidationSchema):
    """Schema for the transaction view."""


class ReservationCreationSchema(Schema):
    """Schema for the reservation creation."""

    establishment_id = fields.Integer(required=True, validate=validate.Range(min=1))
    slot_id = fields.Integer(required=True, validate=validate.Range(min=1))
    plate_number = fields.String(required=True, validate=validate.Length(min=1, max=15))
    vehicle_type_id = fields.Integer(required=True, validate=validate.Range(min=1))
