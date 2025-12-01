"""Test management models"""
from datetime import datetime
from app import db
import uuid

class TestCase(db.Model):
    __tablename__ = 'test_cases'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    protocol_id = db.Column(db.String(36), db.ForeignKey('validation_protocols.id'), nullable=False)
    
    # Test case details
    test_case_id = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    objective = db.Column(db.Text)
    
    # Test type
    test_type = db.Column(db.String(50))  # IQ, OQ, PQ, Integration, UAT
    test_category = db.Column(db.String(100))  # Installation, Configuration, Performance, etc.
    
    # Priority and criticality
    priority = db.Column(db.String(20))  # Critical, High, Medium, Low
    is_gxp_critical = db.Column(db.Boolean, default=True)
    
    # Test procedure
    prerequisites = db.Column(db.Text)
    test_steps = db.Column(db.JSON)  # Array of step objects
    expected_result = db.Column(db.Text)
    acceptance_criteria = db.Column(db.Text)
    
    # Execution
    status = db.Column(db.String(50), default='Not Executed')  # Not Executed, Passed, Failed, Blocked, Deferred
    actual_result = db.Column(db.Text)
    executed_at = db.Column(db.DateTime)
    executed_by = db.Column(db.String(36), db.ForeignKey('users.id'))
    
    # Deviations
    has_deviation = db.Column(db.Boolean, default=False)
    deviation_id = db.Column(db.String(36), db.ForeignKey('deviations.id'))
    
    # Evidence
    evidence_files = db.Column(db.JSON)  # Array of file paths/URLs
    screenshots = db.Column(db.JSON)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    protocol = db.relationship('ValidationProtocol', back_populates='test_cases')
    requirements = db.relationship('Requirement', secondary='requirement_test_mapping', back_populates='test_cases')

class Deviation(db.Model):
    __tablename__ = 'deviations'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    deviation_number = db.Column(db.String(50), unique=True, nullable=False)
    
    # Details
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    deviation_type = db.Column(db.String(50))  # Test Failure, Document Error, Process Deviation
    
    # Impact assessment
    impact_level = db.Column(db.String(20))  # Critical, Major, Minor
    gxp_impact = db.Column(db.Boolean, default=True)
    
    # Root cause analysis
    root_cause = db.Column(db.Text)
    investigation_summary = db.Column(db.Text)
    
    # CAPA
    corrective_action = db.Column(db.Text)
    preventive_action = db.Column(db.Text)
    capa_status = db.Column(db.String(50))  # Open, In Progress, Completed, Verified
    
    # Status
    status = db.Column(db.String(50), default='Open')  # Open, Under Investigation, Closed
    
    # Dates
    reported_date = db.Column(db.Date, default=datetime.utcnow)
    target_close_date = db.Column(db.Date)
    actual_close_date = db.Column(db.Date)
    
    # Ownership
    reported_by = db.Column(db.String(36), db.ForeignKey('users.id'))
    assigned_to = db.Column(db.String(36), db.ForeignKey('users.id'))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)