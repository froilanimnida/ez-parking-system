"""Establishment Document Model."""

from typing import overload

from sqlalchemy import (
    BigInteger, CheckConstraint, Column, ForeignKey, Integer, String, Text, TIMESTAMP, func, text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.utils.db import session_scope


# pylint: disable=not-callable


class EstablishmentDocument(Base):  # pylint: disable=too-few-public-methods
    """Establishment Document Model."""
    __tablename__ = "establishment_document"
    __table_args__ = (
        CheckConstraint(
            "document_type IN ('gov_id', 'parking_photos', 'proof_of_ownership', 'business_certificate', 'bir_certificate', 'liability_insurance')",  # pylint: disable=line-too-long
            name="establishment_document_document_type_check",
        ),
        CheckConstraint(
            "status IN ('pending', 'approved', 'rejected')",
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
    document_type = Column(String(50), nullable=False)
    bucket_path = Column(Text, nullable=False)
    filename = Column(Text, nullable=False)
    mime_type = Column(String(100), nullable=True)
    file_size = Column(BigInteger, nullable=True)
    uploaded_at = Column(TIMESTAMP(timezone=False), nullable=True, server_default=func.now())
    verified_at = Column(TIMESTAMP(timezone=False), nullable=True)
    verified_by = Column(
        Integer,
        ForeignKey("user.user_id", ondelete="NO ACTION", onupdate="NO ACTION"),
        nullable=True,
    )
    status = Column(
        String(20),
        nullable=True,
        server_default=text("'pending'::character varying"),
    )

    verification_notes = Column(Text, nullable=True)
    user = relationship("User", back_populates="establishment_documents")
    parking_establishment = relationship("ParkingEstablishment", back_populates="documents")

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
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None,
            "verified_at": self.verified_at.isoformat() if self.verified_at else None,
            "verified_by": self.verified_by,
            "status": self.status,
            "verification_notes": self.verification_notes,
        }

class EstablishmentDocumentRepository:
    """Repository for establishment document model."""

    @staticmethod
    def create_establishment_document(data: dict):
        """Create a new establishment document."""
        with session_scope() as session:
            new_document = EstablishmentDocument(**data)
            session.add(new_document)
            session.flush()
            session.refresh(new_document)
            return new_document
    @staticmethod
    @overload
    def get_document(document_id: int):
        """Get establishment document by document id."""
    @staticmethod
    @overload
    def get_document(uuid: str):
        """Get establishment document by uuid."""
    @staticmethod
    def get_document(document_id: int = None, uuid: str = None) -> dict:
        """Get establishment document by document id or uuid."""
        with session_scope() as session:
            if document_id:
                document = session.query(EstablishmentDocument).get(document_id)
            else:
                document = session.query(EstablishmentDocument).filter_by(uuid=uuid).first()
            return document.to_dict() if document else {}
    @staticmethod
    def get_establishment_documents(establishment_id: int) -> list[dict]:
        """Get all establishment documents by establishment id."""
        with session_scope() as session:
            documents = session.query(EstablishmentDocument
                ).filter_by(establishment_id=establishment_id).all()
            return [document.to_dict() for document in documents]
    @staticmethod
    def update_document(document_id: int, data: dict):
        """Update an establishment document."""
        with session_scope() as session:
            document = session.query(EstablishmentDocument).get(document_id)
            for key, value in data.items():
                setattr(document, key, value)
            session.commit()
