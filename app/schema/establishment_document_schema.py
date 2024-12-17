""" Wrapper for the establishment document schema. """

from marshmallow import Schema, fields


class EstablishmentDocumentBaseSchema(Schema):
    """ Base schema for establishment document. """
    document_uuid = fields.Str(required=True, validate=[fields.validate.Length(equal=36)])
