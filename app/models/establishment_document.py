"""This module contains the SQLAlchemy model for the establishment_document table."""

# pylint disable=E1102

from enum import Enum as PyEnum

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Column,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    TIMESTAMP,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.utils.db import session_scope


class DocumentTypeEnum(str, PyEnum):
    """Encapsulate enumerate types of document types."""
    GOV_ID = "gov_id"
    PARKING_PHOTOS = "parking_photos"
    PROOF_OF_OWNERSHIP = "proof_of_ownership"
    BUSINESS_CERTIFICATE = "business_certificate"
    BIR_CERTIFICATE = "bir_certificate"
    LIABILITY_INSURANCE = "liability_insurance"


class DocumentStatusEnum(str, PyEnum):
    """Encapsulate enumerate types of document status."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class EstablishmentDocument(Base):
    """Establishment Document Model."""
    __tablename__ = "establishment_document"
    __table_args__ = (
        CheckConstraint(
            f"document_type IN ('{DocumentTypeEnum.GOV_ID}', '{DocumentTypeEnum.PARKING_PHOTOS}', "
            f"'{DocumentTypeEnum.PROOF_OF_OWNERSHIP}', '{DocumentTypeEnum.BUSINESS_CERTIFICATE}', "
            f"'{DocumentTypeEnum.BIR_CERTIFICATE}', '{DocumentTypeEnum.LIABILITY_INSURANCE}')",
            name="establishment_document_document_type_check",
        ),
        CheckConstraint(
            f"status IN ('{DocumentStatusEnum.PENDING}', '{DocumentStatusEnum.APPROVED}', '{DocumentStatusEnum.REJECTED}')",
            name="establishment_document_status_check",
        ),
        {'schema': 'public'},
    )

    document_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        server_default=text("nextval('establishment_document_document_id_seq'::regclass)"),
    )
    uuid = Column(
        UUID(as_uuid=True),
        unique=True,
        nullable=False,
        default=func.uuid_generate_v4(),
    )
    establishment_id = Column(
        Integer,
        ForeignKey("parking_establishment.establishment_id", ondelete="CASCADE"),
        nullable=True,
    )
    document_type = Column(
        Enum(DocumentTypeEnum),
        nullable=False,
    )
    bucket_path = Column(Text, nullable=False)
    filename = Column(Text, nullable=False)
    mime_type = Column(String(100), nullable=True)
    file_size = Column(BigInteger, nullable=True)
    uploaded_at = Column(
        TIMESTAMP(timezone=False),
        nullable=True,
        server_default=func.now(),
    )
    verified_at = Column(TIMESTAMP(timezone=False), nullable=True)
    verified_by = Column(
        Integer,
        ForeignKey("user.user_id", ondelete="NO ACTION", onupdate="NO ACTION"),
        nullable=True,
    )
    status = Column(
        Enum(DocumentStatusEnum),
        nullable=True,
        server_default=text("'pending'::character varying"),
    )
    verification_notes = Column(Text, nullable=True)

    user = relationship("User", backref="establishment_document")

    def to_dict(self):
        """Convert the establishment document object to a dictionary."""
        if self is None:
            return {}
        return {
            "document_id": self.document_id,
            "uuid": str(self.uuid),
            "establishment_id": self.establishment_id,
            "document_type": self.document_type,
            "bucket_path": self.bucket_path,
            "filename": self.filename,
            "mime_type": self.mime_type,
            "file_size": self.file_size,
            "uploaded_at": self.uploaded_at,
            "verified_at": self.verified_at,
            "verified_by": self.verified_by,
            "status": self.status,
            "verification_notes": self.verification_notes,
        }


class EstablishmentDocumentRepository:
    """Repository for establishment document model."""

    @staticmethod
    def create_establishment_document(data):
        """Create a new establishment document."""
        with session_scope() as session:
            new_document = EstablishmentDocument(**data)
            session.add(new_document)
            session.flush()
            return new_document

    @staticmethod
    def get_establishment_documents(establishment_id):
        """Get all establishment documents by establishment id."""
        with session_scope() as session:
            document = session.query(EstablishmentDocument
                ).filter_by(establishment_id=establishment_id).all()
            return document.to_dict()
