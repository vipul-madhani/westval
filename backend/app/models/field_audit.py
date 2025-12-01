from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Text, Boolean, JSON, Index, ForeignKey
from sqlalchemy.orm import relationship
from app import db
import hashlib
import json

class FieldAuditLog(db.Model):
    """Immutable audit trail for field-level changes with cryptographic integrity."""
    __tablename__ = 'field_audit_logs'
    
    id = Column(Integer, primary_key=True)
    entity_type = Column(String(100), nullable=False)  # e.g., 'validation', 'protocol', 'test'
    entity_id = Column(Integer, nullable=False)
    field_name = Column(String(255), nullable=False)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    change_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    ip_address = Column(String(45), nullable=True)  # IPv6 support
    change_reason = Column(Text, nullable=True)
    approval_status = Column(String(50), default='pending')  # pending, approved, rejected
    approved_by = Column(Integer, ForeignKey('user.id'), nullable=True)
    approval_timestamp = Column(DateTime, nullable=True)
    change_hash = Column(String(256), nullable=False, unique=True)  # SHA-256 hash
    previous_hash = Column(String(256), nullable=True)  # Hash chain for integrity
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship('User', foreign_keys=[user_id])
    approver = relationship('User', foreign_keys=[approved_by])
    
    __table_args__ = (
        Index('idx_entity', 'entity_type', 'entity_id'),
        Index('idx_user_timestamp', 'user_id', 'change_timestamp'),
        Index('idx_field_change', 'field_name', 'change_timestamp'),
    )
    
    def calculate_hash(self):
        """Calculate SHA-256 hash for immutability verification."""
        data = f"{self.entity_type}:{self.entity_id}:{self.field_name}:{self.old_value}:{self.new_value}:{self.user_id}:{self.change_timestamp}:{self.previous_hash}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def verify_integrity(self):
        """Verify hash integrity of audit log."""
        return self.change_hash == self.calculate_hash()

class ChangeRequest(db.Model):
    """Change management system with workflow integration."""
    __tablename__ = 'change_requests'
    
    id = Column(Integer, primary_key=True)
    change_number = Column(String(50), unique=True, nullable=False)  # CR-2025-001
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    change_type = Column(String(50), nullable=False)  # minor, major, emergency
    priority = Column(String(50), nullable=False)  # low, medium, high, critical
    status = Column(String(50), default='draft')  # draft, submitted, approved, implemented, closed
    requested_by = Column(Integer, ForeignKey('user.id'), nullable=False)
    assigned_to = Column(Integer, ForeignKey('user.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    submitted_at = Column(DateTime, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    implemented_at = Column(DateTime, nullable=True)
    impact_assessment = Column(JSON, nullable=True)  # { 'systems': [...], 'documents': [...], 'tests': [...] }
    implementation_plan = Column(JSON, nullable=True)
    external_change_id = Column(String(100), nullable=True)  # SAP/JIRA reference
    external_source = Column(String(50), nullable=True)  # 'sap', 'jira', 'manual'
    
    requester = relationship('User', foreign_keys=[requested_by])
    assignee = relationship('User', foreign_keys=[assigned_to])
    
    __table_args__ = (
        Index('idx_status_created', 'status', 'created_at'),
        Index('idx_external_id', 'external_change_id'),
    )

class DocumentComment(db.Model):
    """Threaded comments and collaboration for documents and validations."""
    __tablename__ = 'document_comments'
    
    id = Column(Integer, primary_key=True)
    entity_type = Column(String(100), nullable=False)  # validation, protocol, test_case
    entity_id = Column(Integer, nullable=False)
    parent_comment_id = Column(Integer, ForeignKey('document_comments.id'), nullable=True)  # For threading
    comment_text = Column(Text, nullable=False)
    comment_author_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_resolved = Column(Boolean, default=False)
    resolution_notes = Column(Text, nullable=True)
    resolved_by = Column(Integer, ForeignKey('user.id'), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    attachments = Column(JSON, nullable=True)  # [{ 'filename': '...', 'url': '...', 'size': ... }]
    mentions = Column(JSON, nullable=True)  # [user_id, user_id, ...]
    
    author = relationship('User', foreign_keys=[comment_author_id])
    resolver = relationship('User', foreign_keys=[resolved_by])
    children = relationship('DocumentComment', remote_side=[id])
    
    __table_args__ = (
        Index('idx_entity_comment', 'entity_type', 'entity_id', 'created_at'),
        Index('idx_thread', 'parent_comment_id'),
    )

class RiskAssessment(db.Model):
    """Risk assessment and FMEA (Failure Mode and Effects Analysis)."""
    __tablename__ = 'risk_assessments'
    
    id = Column(Integer, primary_key=True)
    risk_id = Column(String(50), unique=True, nullable=False)  # RA-2025-001
    validation_id = Column(Integer, ForeignKey('validation.id'), nullable=False)
    risk_description = Column(Text, nullable=False)
    risk_category = Column(String(100), nullable=False)  # equipment, process, data, cyber, compliance
    severity = Column(Integer, nullable=False)  # 1-10 scale
    probability = Column(Integer, nullable=False)  # 1-10 scale
    risk_priority_number = Column(Integer, nullable=False)  # severity * probability
    current_controls = Column(JSON, nullable=True)  # Existing mitigations
    mitigation_actions = Column(JSON, nullable=True)  # Recommended actions
    residual_risk = Column(Integer, nullable=True)  # After mitigation
    status = Column(String(50), default='open')  # open, mitigated, closed, accepted
    owner_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    validation = relationship('Validation')
    owner = relationship('User')
    
    __table_args__ = (
        Index('idx_validation_risk', 'validation_id', 'status'),
        Index('idx_risk_priority', 'risk_priority_number'),
    )
