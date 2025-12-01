"""Validation project and protocol models"""
from datetime import datetime
from app import db
import uuid

class ValidationProject(db.Model):
    __tablename__ = 'validation_projects'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_number = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    
    # Classification
    validation_type = db.Column(db.String(50))  # CSV, Lab, Cleaning, Process, Equipment
    methodology = db.Column(db.String(50))  # Waterfall, Agile, CSA, Hybrid
    gamp_category = db.Column(db.String(10))  # Category 1-5
    
    # Risk Assessment
    risk_level = db.Column(db.String(20))  # Low, Medium, High, Critical
    risk_score = db.Column(db.Integer)
    
    # Status
    status = db.Column(db.String(50), default='Planning')  # Planning, In Progress, Testing, Review, Approved, Closed
    
    # Ownership
    owner_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    department = db.Column(db.String(100))
    
    # Dates
    planned_start_date = db.Column(db.Date)
    planned_end_date = db.Column(db.Date)
    actual_start_date = db.Column(db.Date)
    actual_end_date = db.Column(db.Date)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.String(36), db.ForeignKey('users.id'))
    
    # Relationships
    protocols = db.relationship('ValidationProtocol', back_populates='project', cascade='all, delete-orphan')
    requirements = db.relationship('Requirement', back_populates='project', cascade='all, delete-orphan')
    risks = db.relationship('RiskAssessment', back_populates='project', cascade='all, delete-orphan')

class ValidationProtocol(db.Model):
    __tablename__ = 'validation_protocols'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = db.Column(db.String(36), db.ForeignKey('validation_projects.id'), nullable=False)
    
    # Protocol details
    protocol_number = db.Column(db.String(50), unique=True, nullable=False)
    protocol_type = db.Column(db.String(50))  # VMP, IQ, OQ, PQ, VP, Summary Report
    title = db.Column(db.String(255), nullable=False)
    version = db.Column(db.String(20), default='1.0')
    
    # Content
    objective = db.Column(db.Text)
    scope = db.Column(db.Text)
    acceptance_criteria = db.Column(db.Text)
    
    # Status
    status = db.Column(db.String(50), default='Draft')  # Draft, Review, Approved, Executed, Completed
    
    # Document metadata
    template_id = db.Column(db.String(36), db.ForeignKey('document_templates.id'))
    file_path = db.Column(db.String(500))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    approved_at = db.Column(db.DateTime)
    
    # Relationships
    project = db.relationship('ValidationProject', back_populates='protocols')
    test_cases = db.relationship('TestCase', back_populates='protocol', cascade='all, delete-orphan')
    signatures = db.relationship('ElectronicSignature', back_populates='protocol')