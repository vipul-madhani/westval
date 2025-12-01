from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ReportTemplate(Base):
    """Report template configuration for VSR, RTM, OQ/IQ/PQ reports"""
    __tablename__ = 'report_templates'
    
    id = Column(String(36), primary_key=True)
    name = Column(String(100), nullable=False)
    report_type = Column(String(50), nullable=False)  # VSR, RTM, OQ, IQ, PQ
    description = Column(Text)
    template_config = Column(JSON)  # Dynamic template configuration
    sections = Column(JSON)  # Report sections configuration
    export_formats = Column(JSON)  # [PDF, Excel, HTML]
    created_by = Column(String(36), ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    reports = relationship('Report', back_populates='template')
    __table_args__ = (Index('idx_report_type', 'report_type'),)

class Report(Base):
    """Generated reports with metadata and audit trails"""
    __tablename__ = 'reports'
    
    id = Column(String(36), primary_key=True)
    template_id = Column(String(36), ForeignKey('report_templates.id'), nullable=False)
    validation_scope_id = Column(String(36), ForeignKey('validation_scopes.id'))
    report_type = Column(String(50), nullable=False)  # VSR, RTM, OQ, IQ, PQ
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(50), default='DRAFT')  # DRAFT, GENERATING, COMPLETE, FAILED
    content = Column(JSON)  # Full report content
    summary = Column(JSON)  # Report summary/metrics
    generated_by = Column(String(36), ForeignKey('users.id'), nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow)
    approved_by = Column(String(36), ForeignKey('users.id'))
    approved_at = Column(DateTime)
    approval_notes = Column(Text)
    version = Column(Integer, default=1)
    is_published = Column(Boolean, default=False)
    published_at = Column(DateTime)
    expiry_date = Column(DateTime)  # Compliance expiry tracking
    file_path = Column(String(255))  # Path to stored report file
    file_format = Column(String(20))  # pdf, xlsx, html
    file_size = Column(Integer)  # Bytes
    
    template = relationship('ReportTemplate', back_populates='reports')
    exports = relationship('ReportExport', back_populates='report')
    audit_trail = relationship('ReportAudit', back_populates='report')
    __table_args__ = (
        Index('idx_status', 'status'),
        Index('idx_report_type', 'report_type'),
        Index('idx_scope_id', 'validation_scope_id'),
        Index('idx_generated_at', 'generated_at'),
    )

class RequirementTraceabilityMatrix(Base):
    """RTM linking requirements to tests to results"""
    __tablename__ = 'rtm_records'
    
    id = Column(String(36), primary_key=True)
    requirement_id = Column(String(36), ForeignKey('requirements.id'), nullable=False)
    test_plan_id = Column(String(36), ForeignKey('test_plans.id'))
    test_case_id = Column(String(36), ForeignKey('test_cases.id'))
    validation_scope_id = Column(String(36), ForeignKey('validation_scopes.id'), nullable=False)
    requirement_status = Column(String(50))  # OPEN, IN_TEST, VERIFIED, FAILED
    test_status = Column(String(50))  # NOT_EXECUTED, PASSED, FAILED, BLOCKED
    coverage_percentage = Column(Float)  # 0-100
    verification_method = Column(String(100))  # Analysis, Inspection, Test, Demo
    verification_date = Column(DateTime)
    verified_by = Column(String(36), ForeignKey('users.id'))
    risk_level = Column(String(20))  # LOW, MEDIUM, HIGH, CRITICAL
    traceability_notes = Column(Text)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_requirement_id', 'requirement_id'),
        Index('idx_test_case_id', 'test_case_id'),
        Index('idx_scope_coverage', 'validation_scope_id', 'coverage_percentage'),
    )

class ValidationSummary(Base):
    """OQ/IQ/PQ validation summary metrics"""
    __tablename__ = 'validation_summaries'
    
    id = Column(String(36), primary_key=True)
    validation_scope_id = Column(String(36), ForeignKey('validation_scopes.id'), nullable=False)
    validation_phase = Column(String(20), nullable=False)  # OQ, IQ, PQ
    total_requirements = Column(Integer, default=0)
    verified_requirements = Column(Integer, default=0)
    failed_requirements = Column(Integer, default=0)
    total_test_cases = Column(Integer, default=0)
    passed_test_cases = Column(Integer, default=0)
    failed_test_cases = Column(Integer, default=0)
    blocked_test_cases = Column(Integer, default=0)
    overall_compliance_percentage = Column(Float)  # 0-100
    risk_assessment_summary = Column(JSON)  # Risk counts by level
    critical_findings_count = Column(Integer, default=0)
    major_findings_count = Column(Integer, default=0)
    minor_findings_count = Column(Integer, default=0)
    open_issues = Column(Integer, default=0)
    closed_issues = Column(Integer, default=0)
    phase_status = Column(String(50))  # NOT_STARTED, IN_PROGRESS, COMPLETED, ON_HOLD
    phase_completion_date = Column(DateTime)
    phase_completed_by = Column(String(36), ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_scope_phase', 'validation_scope_id', 'validation_phase'),
        Index('idx_phase_status', 'phase_status'),
    )

class ReportExport(Base):
    """Track report exports for compliance and audit"""
    __tablename__ = 'report_exports'
    
    id = Column(String(36), primary_key=True)
    report_id = Column(String(36), ForeignKey('reports.id'), nullable=False)
    export_format = Column(String(20), nullable=False)  # pdf, xlsx, html
    export_file_path = Column(String(255))
    export_size_bytes = Column(Integer)
    exported_by = Column(String(36), ForeignKey('users.id'), nullable=False)
    exported_at = Column(DateTime, default=datetime.utcnow)
    digital_signature = Column(Text)  # For 21 CFR Part 11 compliance
    signature_algorithm = Column(String(50))
    expiration_date = Column(DateTime)
    download_count = Column(Integer, default=0)
    last_downloaded = Column(DateTime)
    
    report = relationship('Report', back_populates='exports')
    __table_args__ = (Index('idx_export_format', 'export_format'),)

class ReportAudit(Base):
    """Complete audit trail for all report operations"""
    __tablename__ = 'report_audit_trail'
    
    id = Column(String(36), primary_key=True)
    report_id = Column(String(36), ForeignKey('reports.id'), nullable=False)
    action = Column(String(50), nullable=False)  # CREATE, MODIFY, APPROVE, EXPORT, DELETE
    action_by_user = Column(String(36), ForeignKey('users.id'), nullable=False)
    action_timestamp = Column(DateTime, default=datetime.utcnow)
    old_values = Column(JSON)  # Previous state
    new_values = Column(JSON)  # New state
    action_reason = Column(Text)
    ip_address = Column(String(45))  # IPv4 or IPv6
    user_agent = Column(String(255))
    # Cryptographic fields for 21 CFR Part 11 compliance
    hash_value = Column(String(64))  # SHA256 hash
    signature = Column(Text)
    
    report = relationship('Report', back_populates='audit_trail')
    __table_args__ = (
        Index('idx_report_id', 'report_id'),
        Index('idx_action', 'action'),
        Index('idx_action_timestamp', 'action_timestamp'),
    )

class ReportSchedule(Base):
    """Schedule automated report generation"""
    __tablename__ = 'report_schedules'
    
    id = Column(String(36), primary_key=True)
    template_id = Column(String(36), ForeignKey('report_templates.id'), nullable=False)
    validation_scope_id = Column(String(36), ForeignKey('validation_scopes.id'))
    schedule_name = Column(String(100), nullable=False)
    cron_expression = Column(String(50))  # Cron format
    frequency = Column(String(50))  # DAILY, WEEKLY, MONTHLY, QUARTERLY, ANNUALLY
    last_run = Column(DateTime)
    next_run = Column(DateTime)
    is_enabled = Column(Boolean, default=True)
    auto_publish = Column(Boolean, default=False)
    recipient_emails = Column(JSON)  # List of email recipients
    created_by = Column(String(36), ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (Index('idx_schedule_enabled', 'is_enabled'),)
