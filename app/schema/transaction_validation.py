""" Incoming transaction related validation schema. """

from marshmallow import Schema, fields, validate, post_load

from app.schema.common_schema_validation import (
    TransactionCommonValidationSchema, EstablishmentCommonValidationSchema,
    SlotCommonValidationSchema
)


class CancelReservationSchema(TransactionCommonValidationSchema):
    """Schema for the reservation cancellation."""


class ViewTransactionSchemaSchema(TransactionCommonValidationSchema):
    """Schema for the transaction view."""


class ReservationCreationSchema(SlotCommonValidationSchema):
    """Schema for the reservation creation."""
    duration = fields.Int(required=True)
    duration_type = fields.Str(
        required=True, validate=validate.OneOf(['monthly', 'daily', 'hourly'])
    )
    scheduled_entry_time = fields.DateTime(required=True)
    scheduled_exit_time = fields.DateTime(required=True)
    amount_due = fields.Float(required=True)
    @post_load
    def add_payment_status(self, in_data, **kwargs):  # pylint: disable=unused-argument
        """Add payment status."""
        in_data["payment_status"] = "pending"
        return in_data


class TransactionFormDetailsSchema(EstablishmentCommonValidationSchema):
    """Schema for the transaction form details."""
    slot_uuid = fields.Str(required=True)


class ValidateEntrySchema(Schema):
    """Validation schema for entry validation."""
    qr_content = fields.Str(required=True, validate=validate.Length(min=100, max=1024))

class ValidateTransaction(ValidateEntrySchema):
    """Validation schema for transaction validation."""
    payment_status = fields.Str(required=True, validate=validate.OneOf(['pending', 'paid']))

class ValidateExitTransaction(ValidateTransaction):
    """Validation schema for exit transaction validation."""
    exit_time = fields.DateTime(required=True)
    amount_due = fields.Float(required=True)
    slot_id = fields.Int(required=True)
