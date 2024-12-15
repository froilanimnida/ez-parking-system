"""This module contains the file upload API."""
from io import BytesIO

from flask import send_file
from flask.views import MethodView
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint

from app.models.establishment_document import EstablishmentDocumentRepository
from app.utils.response_util import set_response

file_upload_blp = Blueprint(
    "file_upload",
    __name__,
    url_prefix="/api/v1/file-upload",
    description="File Upload API",
)


@file_upload_blp.route("/upload")
class DownloadDocument(MethodView):
    @file_upload_blp.doc(
        security=[{"Bearer": []}],
        description="Download a document by its ID.",
        responses={
            200: "Document downloaded.",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Document not found.",
            500: "Internal Server Error",
        },
    )
    @jwt_required(False)
    def get(self, document_id, admin_id):  # pylint: disable=unused-argument
        document = EstablishmentDocumentRepository.get_document_by_id(document_id)
        if not document:
            return set_response(404, {"code": "not_found", "message": "Document not found."})
        
        # Assuming `document['content']` contains the bytes of the document
        document_bytes = document['content']
        document_io = BytesIO(document_bytes)
        document_io.seek(0)
        
        return send_file(
            document_io,
            mimetype=document['mimetype'],  # e.g., 'application/pdf' or 'image/jpeg'
            as_attachment=True,
            download_name=document['filename']  # e.g., 'document.pdf'
        )