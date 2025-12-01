"""Audit trail model for 21 CFR Part 11 compliance"""
from datetime import datetime
from app import db
import uuid

class AuditLog(db.Model):
    """Comprehensive audit trail for all system changes"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # WHO: User identification
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    user_name = db.Column(db.String(255), nullable=False)
    user_role = db.Column(db.String(100))
    
    # WHAT: Action details
    action = db.Column(db.String(100), nullable=False)  # CREATE, UPDATE, DELETE, APPROVE, SIGN, etc.
    entity_type = db.Column(db.String(100), nullable=False)  # Document, Protocol, User, etc.
    entity_id = db.Column(db.String(36), nullable=False)
    entity_name = db.Column(db.String(255))
    
    # Details of change
    field_changed = db.Column(db.String(100))
    old_value = db.Column(db.Text)
    new_value = db.Column(db.Text)
    change_description = db.Column(db.Text)
    
    # WHY: Reason for change
    reason = db.Column(db.Text)
    
    # WHEN: Timestamp
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # WHERE: System information
    ip_address = db.Column(db.String(45))
    device_info = db.Column(db.String(255))
    browser_info = db.Column(db.String(255))
    
    # Additional context
    session_id = db.Column(db.String(100))
    request_id = db.Column(db.String(100))
    
    # Data integrity
    checksum = db.Column(db.String(255))  # Hash of the record for tamper detection
    
    # Relationships
    user = db.relationship('User', back_populates='audit_logs')
    
    def __repr__(self):
        return f'<AuditLog {self.user_name} {self.action} {self.entity_type} at {self.timestamp}>'