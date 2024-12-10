""" Incoming transaction related validation schema. """

from marshmallow import Schema, fields, validate

from app.schema.common_schema_validation import (
    TransactionCommonValidation, EstablishmentCommonValidation
)


class CancelReservationSchema(TransactionCommonValidation):
    """Schema for the reservation cancellation."""


class ViewTransactionSchema(TransactionCommonValidation):
    """Schema for the transaction view."""


class ReservationCreationSchema(EstablishmentCommonValidation):
    """Schema for the reservation creation."""
    slot_id = fields.Integer(required=True, validate=validate.Range(min=1))
    vehicle_type_id = fields.Integer(required=True, validate=validate.Range(min=1))


class TransactionFormDetailsSchema(EstablishmentCommonValidation):
    """Schema for the transaction form details."""
    slot_code = fields.Str(required=True)


class ValidateEntrySchema(Schema):
    """Validation schema for entry validation."""
    qr_content = fields.Str(required=True, validate=validate.Length(min=100, max=1024))
