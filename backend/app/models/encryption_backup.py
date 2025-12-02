from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, Enum as SQLEnum, ForeignKey, LargeBinary
from app import db
from app.models.base_model import BaseModel

class EncryptionAlgorithm(Enum):
    AES_256_GCM = "AES-256-GCM"
    AES_256_CBC = "AES-256-CBC"
    ChaCha20 = "ChaCha20"

class BackupStatus(Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    VERIFIED = "VERIFIED"

class BackupLocation(Enum):
    LOCAL = "LOCAL"
    CLOUD_AWS = "CLOUD_AWS"
    CLOUD_AZURE = "CLOUD_AZURE"
    OFFSITE = "OFFSITE"

class DataEncryption(BaseModel):
    __tablename__ = 'data_encryptions'
    record_id = Column(String(128), nullable=False, unique=True)
    record_type = Column(String(50), nullable=False)
    encrypted_data = Column(LargeBinary, nullable=False)
    encryption_key_id = Column(String(128), nullable=False)
    algorithm = Column(SQLEnum(EncryptionAlgorithm), nullable=False)
    initialization_vector = Column(String(256), nullable=False)
    authentication_tag = Column(String(256), nullable=False)
    data_hash_before = Column(String(256), nullable=False)
    data_hash_after = Column(String(256), nullable=False)
    encrypted_by_id = Column(String(128), ForeignKey('users.id'), nullable=False)
    encryption_timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    decryption_attempts = Column(Integer, default=0)
    last_decryption = Column(DateTime, nullable=True)
    is_valid = Column(Boolean, default=True)

class BackupRecord(BaseModel):
    __tablename__ = 'backup_records'
    backup_type = Column(String(50), nullable=False)
    database_name = Column(String(128), nullable=False)
    backup_size_bytes = Column(Integer, nullable=False)
    backup_location = Column(SQLEnum(BackupLocation), nullable=False)
    backup_path = Column(String(512), nullable=False)
    status = Column(SQLEnum(BackupStatus), default=BackupStatus.PENDING)
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    encryption_key_id = Column(String(128), nullable=False)
    encryption_algorithm = Column(SQLEnum(EncryptionAlgorithm), nullable=False)
    backup_checksum = Column(String(256), nullable=False)
    retention_days = Column(Integer, default=30)
    expiry_date = Column(DateTime, nullable=False)
    created_by_id = Column(String(128), ForeignKey('users.id'), nullable=False)
    notes = Column(Text, nullable=True)

class BackupIntegrityLog(BaseModel):
    __tablename__ = 'backup_integrity_logs'
    backup_id = Column(String(128), ForeignKey('backup_records.id'), nullable=False)
    verification_timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    verification_status = Column(String(20), nullable=False)
    checksum_expected = Column(String(256), nullable=False)
    checksum_actual = Column(String(256), nullable=False)
    integrity_verified = Column(Boolean, nullable=False)
    total_files_checked = Column(Integer, nullable=False)
    files_corrupted = Column(Integer, default=0)
    recovery_possible = Column(Boolean, default=True)
    verified_by_id = Column(String(128), ForeignKey('users.id'), nullable=False)
    verification_details = Column(Text, nullable=True)

class EncryptionKey(BaseModel):
    __tablename__ = 'encryption_keys'
    key_identifier = Column(String(128), nullable=False, unique=True)
    algorithm = Column(SQLEnum(EncryptionAlgorithm), nullable=False)
    key_version = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    rotation_date = Column(DateTime, nullable=True)
    expiry_date = Column(DateTime, nullable=True)
    created_by_id = Column(String(128), ForeignKey('users.id'), nullable=False)
    usage_count = Column(Integer, default=0)
    last_used = Column(DateTime, nullable=True)
