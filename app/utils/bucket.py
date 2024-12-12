""" Module to handle transactional-like uploads to R2 """

# pylint: disable=W0718

from io import BytesIO
import logging
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional

import boto3
from botocore.exceptions import ClientError
from flask import current_app


@dataclass
class UploadFile:
    """ Dataclass to represent a file to be uploaded """
    file_path: str
    destination_key: str
    content_type: str = 'application/octet-stream'


class R2TransactionalUpload:
    """ Class to handle transactional-like uploads to R2 """
    def __init__(self):
        """
        Initialize R2 client with credentials
        """
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=current_app.config["R2_ENDPOINT"],
            aws_access_key_id=current_app.config["R2_ACCESS_KEY_ID"],
            aws_secret_access_key=current_app.config["R2_SECRET_ACCESS_KEY"],
            region_name='auto'
        )
        self.bucket_name = current_app.config["R2_BUCKET_NAME"]
        self.logger = logging.getLogger(__name__)

    def upload(self, files: List[UploadFile]) -> Tuple[bool, Dict[str, str], Dict[str, List[str]]]:
        """
        Perform transactional-like upload of multiple files.
        Returns (success_status, error_message_if_any)
        """
        uploaded_keys = []

        try:
            for file in files:
                self.logger.info("Uploading %s to %s", file.file_path, file.destination_key)
                print("Uploading %s to %s", file.file_path, file.destination_key)

                with open(file.file_path, 'rb') as f:
                    self.s3_client.upload_fileobj(
                        f,
                        self.bucket_name,
                        file.destination_key,
                        ExtraArgs={'ContentType': file.content_type}
                    )
                uploaded_keys.append(file.destination_key)

            return (
                True,
                {"message": "All files uploaded successfully"}, {"uploaded_keys": uploaded_keys}
            )

        except Exception as e:
            self.logger.error("Error during upload: %s", str(e))

            self.logger.info("Starting rollback process")

            for key in uploaded_keys:
                try:
                    self.s3_client.delete_object(
                        Bucket=self.bucket_name,
                        Key=key
                    )
                    self.logger.info("Rolled back upload for %s", key)
                except Exception as delete_error:
                    self.logger.error("Error during rollback of %s: %s", key, str(delete_error))

            return False, {"error": str(e)}

    def download(self, key: str) -> Tuple[Optional[BytesIO], Optional[str], Optional[str]]:
        """
        Download a file from R2 bucket and return it as a BytesIO object

        Args:
            key: The key of the file in the bucket

        Returns:
            Tuple of (file_object, content_type, filename)
            Returns (None, None, None) if file not found or error occurs
        """
        try:
            # Get object metadata first to check existence and get content type
            response = self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=key
            )

            # Get the actual object
            file_obj = BytesIO()
            self.s3_client.download_fileobj(
                self.bucket_name,
                key,
                file_obj
            )

            # Reset file pointer to beginning
            file_obj.seek(0)

            content_type = response.get('ContentType', 'application/octet-stream')
            filename = key.split('/')[-1]  # Get filename from key

            return file_obj, content_type, filename

        except ClientError as e:
            self.logger.error("Error downloading file %s: %s", key, str(e))
            return None, None, None
        except Exception as e:
            self.logger.error("Unexpected error downloading file %s: %s", key, str(e))
            return None, None, None

    def verify_uploads(self, keys: List[str]) -> bool:
        """
        Verify that all specified keys exist in the bucket
        """
        try:
            for key in keys:
                self.s3_client.head_object(Bucket=self.bucket_name, Key=key)
            return True
        except ClientError:
            return False
