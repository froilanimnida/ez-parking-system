""" Wrapper for the establishment document schema. """

from marshmallow import Schema, fields


class EstablishmentDocumentBaseSchema(Schema):
    """ Base schema for establishment document. """
    bucket_path = fields.Str(required=True)
