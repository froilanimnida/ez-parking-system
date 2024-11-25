""" Wraps the query validation for banning the plate numbers by the admin. """

from marshmallow import Schema, fields, validate


class BanQueryValidation(Schema):
    """Validation schema for banning the plate numbers by the admin."""

    plate_number = fields.Str(required=True, validate=validate.Length(min=1, max=10))
    reason = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    is_permanent = fields.Bool(required=True)
    banned_by = fields.Int(required=True, validate=validate.Range(min=1))

class UnbanQueryValidation(Schema):
    """Validation schema for unbanning the plate numbers by the admin."""

    plate_number = fields.Str(required=True, validate=validate.Length(min=1, max=10))
    unbanned_by = fields.Int(required=True, validate=validate.Range(min=1))
