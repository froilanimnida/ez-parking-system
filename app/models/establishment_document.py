
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

from app.models.base import Base


class DocumentTypeEnum(str, PyEnum):
    gov_id = "gov_id"
    parking_photos = "parking_photos"
    proof_of_ownership = "proof_of_ownership"
    business_certificate = "business_certificate"
    bir_certificate = "bir_certificate"
    liability_insurance = "liability_insurance"


class DocumentStatusEnum(str, PyEnum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class EstablishmentDocument(Base):
    __tablename__ = "establishment_document"
    
    document_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        server_default=text("nextval('establishment_document_document_id_seq'::regclass)"),
    )
    establishment_id = Column(
        Integer,
        ForeignKey("public.parking_establishment.establishment_id", ondelete="CASCADE"),
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
        ForeignKey("public.user.user_id", ondelete="NO ACTION", onupdate="NO ACTION"),
        nullable=True,
    )
    status = Column(
        Enum(DocumentStatusEnum),
        nullable=True,
        server_default=text("'pending'::character varying"),
    )
    verification_notes = Column(Text, nullable=True)
    
    __table_args__ = (
        {"schema": "public"},
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
        {"schema": "public"},
    )