"""This module contains the file upload API."""

from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint
from werkzeug.utils import secure_filename

from app.schema.parking_manager_validation import FileUploadSchema
from app.schema.response_schema import ApiResponse
from app.utils.response_util import set_response
from app.models.parking_manager_file import ParkingManagerFileRepository

file_upload_blp = Blueprint(
    "file_upload",
    __name__,
    url_prefix="/api/v1/file-upload",
    description="File Upload API",
)


@file_upload_blp.route("/upload")
class FileUpload(MethodView):
    """Handles file uploads."""

    @file_upload_blp.arguments(FileUploadSchema, location="form")
    @file_upload_blp.response(201, ApiResponse)
    def post(self):
        """Upload a file."""
        if "file" not in request.files:
            return set_response(
                400, {"code": "no_file", "message": "No file part in the request"}
            )

        file = request.files["file"]
        if file.filename == "":
            return set_response(
                400, {"code": "no_filename", "message": "No selected file"}
            )

        if file:
            filename = secure_filename(file.filename)

            return set_response(
                201,
                {
                    "code": "upload_success",
                    "message": "File uploaded successfully",
                },
            )
