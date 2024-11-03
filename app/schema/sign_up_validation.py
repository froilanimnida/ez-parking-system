from marshmallow import Schema, fields, validate


class SignUpValidation(Schema):
    """ Class to handle user registration validation. """
    first_name = fields.Str(required=True, validate=validate.Length(min=1))
    last_name = fields.Str(required=True, validate=validate.Length(min=1))
    email = fields.Email(required=True)
    phone_number = fields.Str(required=True, validate=validate.Length(min=10))
    password = fields.Str(required=True, validate=validate.Length(min=8))
