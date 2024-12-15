""" Wraps the logic for fetching establishment documents. """
from io import BytesIO

from app.utils.bucket import R2TransactionalUpload


class EstablishmentDocument:
    """ Wraps the logic for fetching establishment documents. """

    @staticmethod
    def get_document(bucket_path: str) -> BytesIO | tuple[None, None, None]:
        return GetDocument.get_document(bucket_path)
    

class GetDocument:
    """ Wraps the logic for fetching establishment documents. """

    @staticmethod
    def get_document(bucket_path: str) -> BytesIO | tuple[None, None, None]:
        
        r2_instance = R2TransactionalUpload()
        parking_establishment_documents_object = r2_instance.download(bucket_path)
        return parking_establishment_documents_object
        