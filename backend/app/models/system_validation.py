from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from . import db

class ValidationPhase(enum.Enum):
    INSTALLATION_QUALIFICATION = 'IQ'
    OPERATIONAL_QUALIFICATION = 'OQ'
    PERFORMANCE_QUALIFICATION = 'PQ'

class ValidationStatus(enum.Enum):
    PLANNED = 'PLANNED'
    IN_PROGRESS = 'IN_PROGRESS'
    PASSED = 'PASSED'
    FAILED = 'FAILED'
    APPROVED = 'APPROVED'

class ValidationProtocol(db.Model):
    __tablename__ = 'validation_protocols'
    id = Column(Integer, primary_key=True)
    protocol_name = Column(String(255), nullable=False)
    phase = Column(Enum(ValidationPhase), nullable=False)
    status = Column(Enum(ValidationStatus), default=ValidationStatus.PLANNED)
    scope = Column(Text, nullable=False)
    acceptance_criteria = Column(Text, nullable=False)
    created_by_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    approved_by_id = Column(Integer, ForeignKey('user.id'))
    approved_at = Column(DateTime)
    validation_results = relationship('ValidationResult', backref='protocol')
    
class ValidationResult(db.Model):
    __tablename__ = 'validation_results'
    id = Column(Integer, primary_key=True)
    protocol_id = Column(Integer, ForeignKey('validation_protocols.id'), nullable=False)
    test_case = Column(String(255), nullable=False)
    expected_outcome = Column(Text, nullable=False)
    actual_outcome = Column(Text, nullable=False)
    passed = Column(Boolean, nullable=False)
    evidence_location = Column(String(500))
    executed_by_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    executed_at = Column(DateTime, default=datetime.utcnow)
    reviewed_by_id = Column(Integer, ForeignKey('user.id'))
    reviewed_at = Column(DateTime)
    
class ComprehensiveAuditLog(db.Model):
    __tablename__ = 'comprehensive_audit_logs'
    id = Column(Integer, primary_key=True)
    audit_type = Column(String(100), nullable=False)
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(Integer, nullable=False)
    action = Column(String(255), nullable=False)
    old_values = Column(Text)
    new_values = Column(Text)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    checksum = Column(String(256), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
class SystemHealthMetric(db.Model):
    __tablename__ = 'system_health_metrics'
    id = Column(Integer, primary_key=True)
    metric_name = Column(String(255), nullable=False)
    metric_value = Column(Float, nullable=False)
    threshold_min = Column(Float)
    threshold_max = Column(Float)
    status = Column(String(50), default='OK')
    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
