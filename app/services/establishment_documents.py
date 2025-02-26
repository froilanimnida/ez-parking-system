""" Wraps the logic for fetching establishment documents. """
from io import BytesIO

from app.utils.bucket import R2TransactionalUpload


class EstablishmentDocument:  # pylint: disable=missing-function-docstring, too-few-public-methods
    """ Wraps the logic for fetching establishment documents. """
    @staticmethod
    def get_document(bucket_path: str) -> tuple[BytesIO, str, str] | tuple[None, None, None]:
        return GetDocument.get_document(bucket_path)
class GetDocument:  # pylint: disable=missing-function-docstring, too-few-public-methods
    """ Wraps the logic for fetching establishment documents. """
    @staticmethod
    def get_document(bucket_path: str) -> tuple[BytesIO, str, str] | tuple[None, None, None]:
        r2_instance = R2TransactionalUpload()
        parking_establishment_documents_object, content_type, file_name = r2_instance.download(
            bucket_path
        )
        return parking_establishment_documents_object, content_type, file_name
