"""This module contains the SQLAlchemy model for the establishment_document table."""

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
    gov_id = "gov_id"
    parking_photos = "parking_photos"
    proof_of_ownership = "proof_of_ownership"
    business_certificate = "business_certificate"
    bir_certificate = "bir_certificate"
    liability_insurance = "liability_insurance"


class DocumentStatusEnum(str, PyEnum):
    """Encapsulate enumerate types of document status."""
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class EstablishmentDocument(Base):
    __tablename__ = "establishment_document"
    __table_args__ = (
        CheckConstraint(
            f"document_type IN ('{DocumentTypeEnum.gov_id}', '{DocumentTypeEnum.parking_photos}', "
            f"'{DocumentTypeEnum.proof_of_ownership}', '{DocumentTypeEnum.business_certificate}', "
            f"'{DocumentTypeEnum.bir_certificate}', '{DocumentTypeEnum.liability_insurance}')",
            name="establishment_document_document_type_check",
        ),
        CheckConstraint(
            f"status IN ('{DocumentStatusEnum.pending}', '{DocumentStatusEnum.approved}', '{DocumentStatusEnum.rejected}')",
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


class EstablishmentDocumentRepository:
    """Repository for establishment document model."""

    @staticmethod
    def create_establishment_document(data):
        with session_scope() as session:
            new_document = EstablishmentDocument(**data)
            session.add(new_document)
            session.flush()
            return new_document
        
    @staticmethod
    def get_establishment_documents(establishment_id):
        with session_scope() as session:
            return session.query(EstablishmentDocument).filter_by(establishment_id=establishment_id).all()