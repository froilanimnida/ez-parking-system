""" Validation for new establishment data. """

from marshmallow import Schema, fields, validate

class EstablishmentValidation(Schema):
    """ Class to handle parking establishment validation. """
    name = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=255)
    )
    address = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=255)
    )
    contact_number = fields.Str(
        required=True,
        validate=[
            validate.Regexp(
                regex=r'^\+?[1-9]\d{1,14}$',
                error='Invalid phone number format.'
            ),
            validate.Length(min=10, max=15),
        ]
    )
    opening_time = fields.Time(required=True)
    closing_time = fields.Time(required=True )
    is_24_hours = fields.Bool(required=True)
    hourly_rate = fields.Float(required=True)
    longitude = fields.Float(required=True)
    latitude = fields.Float(required=True)
