"""Workflow and task management models"""
from datetime import datetime, timedelta
from app import db
import uuid

class WorkflowDefinition(db.Model):
    """Define workflow templates"""
    __tablename__ = 'workflow_definitions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    entity_type = db.Column(db.String(50))  # Document, Protocol, etc.
    
    # Workflow stages as JSON
    stages = db.Column(db.JSON)  # [{name: 'Author Review', roles: ['author'], order: 1}]
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class WorkflowInstance(db.Model):
    """Active workflow for a specific entity"""
    __tablename__ = 'workflow_instances'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_definition_id = db.Column(db.String(36), db.ForeignKey('workflow_definitions.id'))
    
    # Entity being processed
    entity_type = db.Column(db.String(50), nullable=False)
    entity_id = db.Column(db.String(36), nullable=False)
    
    # Current state
    current_stage = db.Column(db.Integer, default=0)
    status = db.Column(db.String(50), default='IN_PROGRESS')  # IN_PROGRESS, COMPLETED, REJECTED, CANCELLED
    
    # Metadata
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    started_by = db.Column(db.String(36), db.ForeignKey('users.id'))
    
    # Relationships
    tasks = db.relationship('WorkflowTask', back_populates='workflow', cascade='all, delete-orphan')

class WorkflowTask(db.Model):
    """Individual tasks in workflow"""
    __tablename__ = 'workflow_tasks'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_instance_id = db.Column(db.String(36), db.ForeignKey('workflow_instances.id'))
    
    # Task details
    stage_name = db.Column(db.String(100), nullable=False)
    stage_order = db.Column(db.Integer, nullable=False)
    task_type = db.Column(db.String(50))  # REVIEW, APPROVE, TEST, etc.
    
    # Assignment
    assigned_to = db.Column(db.String(36), db.ForeignKey('users.id'))
    assigned_role = db.Column(db.String(50))
    
    # Status
    status = db.Column(db.String(50), default='PENDING')  # PENDING, IN_PROGRESS, COMPLETED, REJECTED
    
    # Actions
    action_taken = db.Column(db.String(50))  # APPROVED, REJECTED, REVIEWED
    comments = db.Column(db.Text)
    
    # Timing
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    # Escalation
    is_overdue = db.Column(db.Boolean, default=False)
    escalated = db.Column(db.Boolean, default=False)
    escalated_to = db.Column(db.String(36), db.ForeignKey('users.id'))
    
    # Relationships
    workflow = db.relationship('WorkflowInstance', back_populates='tasks')

class Notification(db.Model):
    """User notifications"""
    __tablename__ = 'notifications'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Recipient
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    # Notification content
    type = db.Column(db.String(50))  # TASK_ASSIGNED, APPROVAL_REQUIRED, ESCALATION, etc.
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    
    # Link to entity
    entity_type = db.Column(db.String(50))
    entity_id = db.Column(db.String(36))
    
    # Status
    is_read = db.Column(db.Boolean, default=False)
    is_actioned = db.Column(db.Boolean, default=False)
    
    # Timing
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime)
    
    # Priority
    priority = db.Column(db.String(20), default='NORMAL')  # LOW, NORMAL, HIGH, URGENT