from datetime import datetime
from sqlalchemy.dialects.mysql import JSON
from app import db
import uuid

class TestPlan(db.Model):
    __tablename__ = 'test_plans'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = db.Column(db.String(36), db.ForeignKey('validation_projects.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default='Draft')  # Draft, Active, Completed, Archived
    created_by = db.Column(db.String(36), db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    test_sets = db.relationship('TestSet', backref='plan', cascade='all, delete-orphan')
    test_cases = db.relationship('TestCase', backref='plan', cascade='all, delete-orphan')

class TestSet(db.Model):
    __tablename__ = 'test_sets'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plan_id = db.Column(db.String(36), db.ForeignKey('test_plans.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    order_num = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    test_cases = db.relationship('TestCase', backref='test_set', cascade='all, delete-orphan')

class TestCase(db.Model):
    __tablename__ = 'test_cases'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plan_id = db.Column(db.String(36), db.ForeignKey('test_plans.id'), nullable=False)
    set_id = db.Column(db.String(36), db.ForeignKey('test_sets.id'))
    requirement_id = db.Column(db.String(36), db.ForeignKey('requirements.id'))
    
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    preconditions = db.Column(db.Text)
    test_type = db.Column(db.String(50))  # Functional, Performance, Security
    priority = db.Column(db.Integer, default=3)  # 1=Critical, 2=High, 3=Medium, 4=Low
    status = db.Column(db.String(50), default='Draft')  # Draft, Active, Deprecated
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    test_steps = db.relationship('TestStep', backref='test_case', cascade='all, delete-orphan')
    test_executions = db.relationship('TestExecution', backref='test_case')

class TestStep(db.Model):
    __tablename__ = 'test_steps'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    test_case_id = db.Column(db.String(36), db.ForeignKey('test_cases.id'), nullable=False)
    step_number = db.Column(db.Integer, nullable=False)
    action = db.Column(db.Text, nullable=False)
    expected_result = db.Column(db.Text, nullable=False)
    test_data = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    test_results = db.relationship('TestStepResult', backref='step', cascade='all, delete-orphan')

class TestExecution(db.Model):
    __tablename__ = 'test_executions'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    test_case_id = db.Column(db.String(36), db.ForeignKey('test_cases.id'), nullable=False)
    execution_date = db.Column(db.DateTime, default=datetime.utcnow)
    executed_by = db.Column(db.String(36), db.ForeignKey('users.id'))
    
    total_steps = db.Column(db.Integer)
    passed_steps = db.Column(db.Integer, default=0)
    failed_steps = db.Column(db.Integer, default=0)
    
    overall_status = db.Column(db.String(20))  # PASS, FAIL, BLOCKED, NOT_RUN
    comments = db.Column(db.Text)
    
    screenshots = db.Column(JSON)  # [{url, timestamp, annotation}]
    attachments = db.Column(JSON)  # [{filename, url, size}]
    
    defect_linked = db.Column(db.Boolean, default=False)
    defect_ids = db.Column(JSON)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    test_results = db.relationship('TestStepResult', backref='execution', cascade='all, delete-orphan')

class TestStepResult(db.Model):
    __tablename__ = 'test_step_results'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    execution_id = db.Column(db.String(36), db.ForeignKey('test_executions.id'), nullable=False)
    step_id = db.Column(db.String(36), db.ForeignKey('test_steps.id'), nullable=False)
    
    status = db.Column(db.String(20), nullable=False)  # PASS, FAIL, BLOCKED, SKIPPED
    actual_result = db.Column(db.Text)
    notes = db.Column(db.Text)
    duration_seconds = db.Column(db.Integer)
    
    screenshot_urls = db.Column(JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
