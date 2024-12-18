""" This module contains the common schema validation for the application. """


from marshmallow import Schema, fields


class EstablishmentCommonValidationSchema(Schema):
    """
    Common validation schema for establishment. It is used to validate the establishment_uuid.
    """
    establishment_uuid = fields.Str(required=True)

class TransactionCommonValidationSchema(Schema):
    """ Common validation schema for transaction. It is used to validate the transaction_uuid. """
    transaction_uuid = fields.Str(required=True)

class SlotCommonValidationSchema(Schema):
    """ Common validation schema for slot. It is used to validate the slot_uuid. """
    slot_uuid = fields.Str(required=True)
