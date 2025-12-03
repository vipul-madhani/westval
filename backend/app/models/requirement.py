"""Requirements management models"""
from datetime import datetime
from app import db
import uuid

class Requirement(db.Model):
    __tablename__ = 'requirements'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = db.Column(db.String(36), db.ForeignKey('validation_projects.id'), nullable=False)
    
    # Requirement details
    requirement_id = db.Column(db.String(50), unique=True, nullable=False)
    requirement_type = db.Column(db.String(50))  # URS, FS, DS, Business, System
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    # Classification
    category = db.Column(db.String(100))  # Functional, Non-functional, Performance, Security
    priority = db.Column(db.String(20))  # Critical, High, Medium, Low
    criticality = db.Column(db.String(20))  # GxP Critical, Non-GxP Critical, Non-Critical
    
    # Status
    status = db.Column(db.String(50), default='Draft')  # Draft, Approved, Implemented, Verified
    
    # Traceability
    parent_requirement_id = db.Column(db.String(36), db.ForeignKey('requirements.id'))
    source = db.Column(db.String(255))  # Origin of requirement
    rationale = db.Column(db.Text)
    
    # Testing
    test_approach = db.Column(db.Text)
    acceptance_criteria = db.Column(db.Text)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.String(36), db.ForeignKey('users.id'))
    
    # Relationships
    project = db.relationship('ValidationProject', back_populates='requirements')
    # test_cases = db.relationship('TestCase', secondary='requirement_test_mapping', back_populates='requirements')

class RequirementTestMapping(db.Model):
    """Traceability matrix mapping"""
    __tablename__ = 'requirement_test_mapping'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    requirement_id = db.Column(db.String(36), db.ForeignKey('requirements.id'), nullable=False)
    test_case_id = db.Column(db.String(36), db.ForeignKey('test_cases.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)