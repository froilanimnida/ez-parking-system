""" Module to handle transactional-like uploads to R2 """

# pylint: disable=W0718

import logging
from dataclasses import dataclass
from typing import List, Dict, Tuple

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

    def upload(self, files: List[UploadFile]) -> Tuple[bool, Dict[str, str]]:
        """
        Perform transactional-like upload of multiple files.
        Returns (success_status, error_message_if_any)
        """
        uploaded_keys = []

        try:
            # First phase: Upload all files
            for file in files:
                self.logger.info("Uploading %s to %s", file.file_path, file.destination_key)

                with open(file.file_path, 'rb') as f:
                    self.s3_client.upload_fileobj(
                        f,
                        self.bucket_name,
                        file.destination_key,
                        ExtraArgs={'ContentType': file.content_type}
                    )
                uploaded_keys.append(file.destination_key)

            # If we reach here, all uploads were successful
            return True, {"message": "All files uploaded successfully"}

        except Exception as e:
            self.logger.error("Error during upload: %s", str(e))

            # Rollback: Delete any files that were uploaded
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
                    # Continue with other deletions even if one fails

            return False, {"error": str(e)}

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
