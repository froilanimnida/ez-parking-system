import boto3
import uuid
from flask import current_app

class FileUploadService:
    def __init__(self):
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=current_app.config["R2_ENDPOINT_URL"],
            aws_access_key_id=current_app.config["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=current_app.config["AWS_SECRET_ACCESS_KEY"],
            region_name=current_app.config["AWS_REGION"],
        )
        self.bucket_name = current_app.config["R2_BUCKET_NAME"]

    def upload_file(self, file):
        file_extension = file.filename.split('.')[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        self.s3_client.upload_fileobj(file, self.bucket_name, unique_filename)
        file_url = f"{self.s3_client.meta.endpoint_url}/{self.bucket_name}/{unique_filename}"
        return file_url
