"""Risk assessment models"""
from datetime import datetime
from app import db
import uuid

class RiskAssessment(db.Model):
    __tablename__ = 'risk_assessments'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = db.Column(db.String(36), db.ForeignKey('validation_projects.id'), nullable=False)
    
    # Risk details
    risk_id = db.Column(db.String(50), unique=True, nullable=False)
    hazard_description = db.Column(db.Text, nullable=False)
    potential_consequence = db.Column(db.Text)
    
    # Risk scoring
    severity = db.Column(db.Integer)  # 1-5 scale
    probability = db.Column(db.Integer)  # 1-5 scale
    detectability = db.Column(db.Integer)  # 1-5 scale (for FMEA)
    risk_priority_number = db.Column(db.Integer)  # RPN = Severity x Probability x Detectability
    risk_level = db.Column(db.String(20))  # Low, Medium, High, Critical
    
    # Risk categorization
    risk_category = db.Column(db.String(100))  # Patient Safety, Data Integrity, Product Quality
    affected_area = db.Column(db.String(100))
    
    # Mitigation
    existing_controls = db.Column(db.Text)
    mitigation_strategy = db.Column(db.Text)
    residual_risk_level = db.Column(db.String(20))
    residual_rpn = db.Column(db.Integer)
    
    # Status
    status = db.Column(db.String(50), default='Identified')  # Identified, Mitigated, Accepted, Closed
    
    # Ownership
    owner_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = db.relationship('ValidationProject', back_populates='risks')