""" Wraps the logic for fetching establishment documents. """
from io import BytesIO

from app.models.establishment_document import EstablishmentDocumentRepository
from app.utils.bucket import R2TransactionalUpload


class EstablishmentDocument:  # pylint: disable=missing-function-docstring, too-few-public-methods
    """ Wraps the logic for fetching establishment documents. """
    @staticmethod
    def get_document(uuid: str) -> tuple[BytesIO, str, str] | tuple[None, None, None]:
        return GetDocument.get_document(uuid)
class GetDocument:  # pylint: disable=missing-function-docstring, too-few-public-methods
    """ Wraps the logic for fetching establishment documents. """
    @staticmethod
    def get_document(uuid: str) -> tuple[BytesIO, str, str] | tuple[None, None, None]:
        bucket_path = EstablishmentDocumentRepository.get_document(uuid=uuid).get('bucket_path')
        print(f"bucket_path: {bucket_path}")
        r2_instance = R2TransactionalUpload()
        parking_establishment_documents_object, content_type, file_name = r2_instance.download(
            bucket_path
        )
        return parking_establishment_documents_object, content_type, file_name
