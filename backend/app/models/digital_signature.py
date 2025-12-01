from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, Enum as SQLEnum, ForeignKey
from app import db
from app.models.base_model import BaseModel
import json

class SignatureAlgorithm(Enum):
    RSA_2048 = "RSA-2048"
    RSA_4096 = "RSA-4096"
    ECDSA_P256 = "ECDSA-P256"
    ECDSA_P384 = "ECDSA-P384"

class CertificateStatus(Enum):
    VALID = "VALID"
    REVOKED = "REVOKED"
    EXPIRED = "EXPIRED"
    PENDING = "PENDING"

class DigitalCertificate(BaseModel):
    __tablename__ = 'digital_certificates'
    certificate_pem = Column(Text, nullable=False)
    public_key_pem = Column(Text, nullable=False)
    private_key_pem = Column(Text, nullable=True)
    subject_dn = Column(String(512), nullable=False)
    issuer_dn = Column(String(512), nullable=False)
    serial_number = Column(String(128), nullable=False, unique=True)
    issued_date = Column(DateTime, nullable=False)
    expiry_date = Column(DateTime, nullable=False)
    thumbprint = Column(String(128), nullable=False, unique=True)
    algorithm = Column(SQLEnum(SignatureAlgorithm), nullable=False)
    status = Column(SQLEnum(CertificateStatus), default=CertificateStatus.VALID)
    is_ca = Column(Boolean, default=False)
    key_length = Column(Integer, nullable=False)
    user_id = Column(String(128), ForeignKey('users.id'), nullable=True)
    created_by_id = Column(String(128), ForeignKey('users.id'), nullable=False)

class DigitalSignature(BaseModel):
    __tablename__ = 'digital_signatures'
    document_id = Column(String(128), ForeignKey('documents.id'), nullable=False)
    document_type = Column(String(50), nullable=False)
    signature_value = Column(Text, nullable=False)
    signature_hash = Column(String(256), nullable=False, unique=True)
    certificate_id = Column(String(128), ForeignKey('digital_certificates.id'), nullable=False)
    signed_by_id = Column(String(128), ForeignKey('users.id'), nullable=False)
    signature_timestamp = Column(DateTime, nullable=False)
    tsa_timestamp = Column(DateTime, nullable=True)
    tsa_token = Column(Text, nullable=True)
    algorithm = Column(SQLEnum(SignatureAlgorithm), nullable=False)
    is_valid = Column(Boolean, default=True)
    validation_timestamp = Column(DateTime, nullable=True)
    validation_details = Column(Text, nullable=True)
    reason = Column(String(512), nullable=True)
    location = Column(String(256), nullable=True)

class SignatureRevocation(BaseModel):
    __tablename__ = 'signature_revocations'
    certificate_id = Column(String(128), ForeignKey('digital_certificates.id'), nullable=False)
    revoked_at = Column(DateTime, nullable=False)
    revoked_by_id = Column(String(128), ForeignKey('users.id'), nullable=False)
    reason = Column(String(512), nullable=False)
    crl_entry_number = Column(Integer, nullable=False)
    revocation_timestamp = Column(DateTime, nullable=False)
