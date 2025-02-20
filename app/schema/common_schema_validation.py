""" This module contains the common schema validation for the application. """

# pylint: disable=R0801

from marshmallow import Schema, fields, validate


class EstablishmentCommonValidationSchema(Schema):
    """
    Common validation schema for establishment. It is used to validate the establishment_uuid.
    """
    bucket_path = fields.Str(required=True)

class TransactionCommonValidationSchema(Schema):
    """ Common validation schema for transaction. It is used to validate the transaction_uuid. """
    transaction_uuid = fields.Str(required=True)

class SlotCommonValidationSchema(Schema):
    """ Common validation schema for slot. It is used to validate the slot_uuid. """
    slot_uuid = fields.Str(required=True)


class UserUpdateProfileSchema(Schema):
    """ Schema for updating user profile. """
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    middle_name = fields.Str(required=False)
    suffix = fields.Str(required=False)
    phone_number = fields.Str(
        required=True,
        validate=[
            validate.Length(min=10, max=15),
            validate.Regexp(
                regex=r"^\+?[0-9]\d{1,14}$", error="Invalid phone number format."
            ),
        ],
    )
    nickname = fields.Str(required=False, validate=validate.Length(min=3, max=24))
