"""Document management models"""
from datetime import datetime
from app import db
import uuid

class Document(db.Model):
    __tablename__ = 'documents'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_number = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    document_type = db.Column(db.String(50))  # Protocol, SOP, Report, Policy, etc.
    
    # Version control
    version = db.Column(db.String(20), default='1.0')
    is_current_version = db.Column(db.Boolean, default=True)
    parent_document_id = db.Column(db.String(36), db.ForeignKey('documents.id'))  # For version history
    
    # Content
    description = db.Column(db.Text)
    content = db.Column(db.Text)  # JSON or HTML content
    file_path = db.Column(db.String(500))
    file_size = db.Column(db.BigInteger)
    mime_type = db.Column(db.String(100))
    
    # Status and workflow
    status = db.Column(db.String(50), default='Draft')  # Draft, Review, Approved, Obsolete, Archived
    review_due_date = db.Column(db.Date)
    
    # Classification
    category = db.Column(db.String(100))
    tags = db.Column(db.JSON)  # Array of tags
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    approved_at = db.Column(db.DateTime)
    effective_date = db.Column(db.Date)
    expiry_date = db.Column(db.Date)
    
    # Ownership
    owner_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    department = db.Column(db.String(100))
    
    # Compliance
    is_gxp = db.Column(db.Boolean, default=True)
    regulatory_references = db.Column(db.JSON)  # Array of regulatory citations
    
    # Relationships
    signatures = db.relationship('ElectronicSignature', back_populates='document')
    # audit_logs = db.relationship('AuditLog', foreign_keys='AuditLog.entity_id')  # TODO: Fix polymorphic relationship

class DocumentTemplate(db.Model):
    __tablename__ = 'document_templates'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    template_type = db.Column(db.String(50))  # IQ, OQ, PQ, VMP, etc.
    
    # Template content
    content = db.Column(db.Text)  # JSON structure
    file_path = db.Column(db.String(500))
    
    # Configuration
    is_active = db.Column(db.Boolean, default=True)
    is_default = db.Column(db.Boolean, default=False)
    organization_id = db.Column(db.String(36))  # For multi-tenancy
    
    # Metadata
    version = db.Column(db.String(20), default='1.0')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.String(36), db.ForeignKey('users.id'))

class ElectronicSignature(db.Model):
    """21 CFR Part 11 compliant electronic signatures"""
    __tablename__ = 'electronic_signatures'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Signer information
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    signer_name = db.Column(db.String(255), nullable=False)
    signer_role = db.Column(db.String(100))
    
    # Signature details
    signature_meaning = db.Column(db.String(255), nullable=False)  # e.g., "Reviewed and Approved"
    signature_type = db.Column(db.String(50))  # Author, Reviewer, Approver, etc.
    reason = db.Column(db.Text)  # Reason for signing
    
    # Document references
    document_id = db.Column(db.String(36), db.ForeignKey('documents.id'))
    protocol_id = db.Column(db.String(36), db.ForeignKey('validation_protocols.id'))
    entity_type = db.Column(db.String(50))  # Document type being signed
    entity_id = db.Column(db.String(36))  # Generic reference
    
    # Security
    signature_hash = db.Column(db.String(255))  # Cryptographic hash
    ip_address = db.Column(db.String(45))
    device_info = db.Column(db.String(255))
    
    # Timestamp
    signed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = db.relationship('User', back_populates='signatures')
    document = db.relationship('Document', back_populates='signatures')
    protocol = db.relationship('ValidationProtocol', back_populates='signatures')