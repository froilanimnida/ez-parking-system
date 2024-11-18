""" Incoming transaction related validation schema. """

from marshmallow import Schema, fields, validate


class ReservationCreationSchema(Schema):
    """Schema for the reservation creation."""

    establishment_id = fields.Integer(required=True, validate=validate.Range(min=1))
