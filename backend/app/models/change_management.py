from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Text, Boolean, JSON, ForeignKey, desc
from sqlalchemy.orm import relationship
from app import db

class ChangeRequestWorkflow(db.Model):
    __tablename__ = 'change_request_workflows'
    id = Column(Integer, primary_key=True)
    cr_id = Column(Integer, ForeignKey('change_requests.id'), nullable=False)
    stage = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False)
    assigned_to = Column(Integer, ForeignKey('user.id'), nullable=True)
    action_taken_by = Column(Integer, ForeignKey('user.id'), nullable=True)
    action_timestamp = Column(DateTime, nullable=True)
    comments = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    cr = relationship('ChangeRequest')
    assignee = relationship('User', foreign_keys=[assigned_to])
    actor = relationship('User', foreign_keys=[action_taken_by])

class ChangeImpactAssessment(db.Model):
    __tablename__ = 'change_impact_assessments'
    id = Column(Integer, primary_key=True)
    cr_id = Column(Integer, ForeignKey('change_requests.id'), nullable=False)
    affected_systems = Column(JSON, nullable=True)
    affected_documents = Column(JSON, nullable=True)
    affected_tests = Column(JSON, nullable=True)
    risk_level = Column(String(50), nullable=False)
    mitigation_plan = Column(Text, nullable=True)
    testing_scope = Column(JSON, nullable=True)
    rollback_plan = Column(Text, nullable=True)
    assessment_by = Column(Integer, ForeignKey('user.id'), nullable=False)
    assessment_date = Column(DateTime, default=datetime.utcnow)
    cr = relationship('ChangeRequest')
    assessor = relationship('User')

class ChangeImplementationPlan(db.Model):
    __tablename__ = 'change_implementation_plans'
    id = Column(Integer, primary_key=True)
    cr_id = Column(Integer, ForeignKey('change_requests.id'), nullable=False)
    implementation_steps = Column(JSON, nullable=True)
    resource_requirements = Column(JSON, nullable=True)
    timeline = Column(JSON, nullable=True)
    responsible_party = Column(Integer, ForeignKey('user.id'), nullable=False)
    status = Column(String(50), default='pending')
    completion_percentage = Column(Integer, default=0)
    blockers = Column(JSON, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    cr = relationship('ChangeRequest')
    responsible_user = relationship('User')

class ApprovalWorkflow(db.Model):
    __tablename__ = 'approval_workflows'
    id = Column(Integer, primary_key=True)
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(Integer, nullable=False)
    approval_chain = Column(JSON, nullable=False)
    current_stage = Column(Integer, default=0)
    overall_status = Column(String(50), default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)
    created_by = Column(Integer, ForeignKey('user.id'), nullable=False)
    creator = relationship('User')
