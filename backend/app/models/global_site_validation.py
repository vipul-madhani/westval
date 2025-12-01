from app import db
from datetime import datetime
from uuid import uuid4
import json

class ValidationScope(db.Model):
    """Master validation scope - can be GLOBAL or SITE"""
    __tablename__ = 'validation_scopes'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    validation_id = db.Column(db.String(36), db.ForeignKey('validations.id'), nullable=False)
    scope_type = db.Column(db.String(20), nullable=False)  # GLOBAL or SITE
    scope_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    parent_scope_id = db.Column(db.String(36), db.ForeignKey('validation_scopes.id'), nullable=True)
    
    # Inheritance settings
    inherit_requirements = db.Column(db.Boolean, default=True)
    inherit_tests = db.Column(db.Boolean, default=True)
    inherit_risks = db.Column(db.Boolean, default=True)
    
    # Customization tracking
    customizations = db.Column(db.JSON, default={})  # Track what's been customized
    is_locked = db.Column(db.Boolean, default=False)  # Lock when published
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.String(36), db.ForeignKey('users.id'))
    
    # Relationships
    validation = db.relationship('Validation', backref='scopes')
    parent_scope = db.relationship('ValidationScope', remote_side=[id], backref='child_scopes')
    child_scopes = db.relationship('ValidationScope', remote_side='ValidationScope.parent_scope_id')
    test_templates = db.relationship('TestTemplate', backref='scope', cascade='all, delete-orphan')
    requirement_mappings = db.relationship('RequirementMapping', backref='scope', cascade='all, delete-orphan')
    
    __table_args__ = (
        db.Index('idx_validation_id', 'validation_id'),
        db.Index('idx_scope_type', 'scope_type'),
    )

class TestTemplate(db.Model):
    """Template test case for global/site inheritance"""
    __tablename__ = 'test_templates'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    scope_id = db.Column(db.String(36), db.ForeignKey('validation_scopes.id'), nullable=False)
    parent_template_id = db.Column(db.String(36), db.ForeignKey('test_templates.id'), nullable=True)
    
    test_case_id = db.Column(db.String(36), db.ForeignKey('test_cases.id'))
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    
    # Template metadata
    is_global_template = db.Column(db.Boolean, default=False)
    is_inherited = db.Column(db.Boolean, default=False)
    customization_allowed = db.Column(db.Boolean, default=True)
    
    # Customizations applied at this level
    customizations = db.Column(db.JSON, default={})  # Fields that have been customized
    override_fields = db.Column(db.JSON, default={})  # Specific field overrides
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    scope = db.relationship('ValidationScope', backref='templates')
    parent_template = db.relationship('TestTemplate', remote_side=[id], backref='child_templates')
    child_templates = db.relationship('TestTemplate', remote_side='TestTemplate.parent_template_id')
    test_case = db.relationship('TestCase')
    site_instances = db.relationship('TestSiteInstance', backref='template', cascade='all, delete-orphan')
    
    __table_args__ = (
        db.Index('idx_scope_id', 'scope_id'),
        db.Index('idx_is_global', 'is_global_template'),
    )

class TestSiteInstance(db.Model):
    """Site-specific instance of a global test template"""
    __tablename__ = 'test_site_instances'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    template_id = db.Column(db.String(36), db.ForeignKey('test_templates.id'), nullable=False)
    site_scope_id = db.Column(db.String(36), db.ForeignKey('validation_scopes.id'), nullable=False)
    
    # Instance data
    test_case_id = db.Column(db.String(36), db.ForeignKey('test_cases.id'))
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    
    # Site-specific customizations
    customizations = db.Column(db.JSON, default={})  # What's different from global
    overrides = db.Column(db.JSON, default={})  # Specific field value overrides
    sync_status = db.Column(db.String(20), default='SYNCED')  # SYNCED, OUT_OF_SYNC, CUSTOM
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    template = db.relationship('TestTemplate')
    site_scope = db.relationship('ValidationScope')
    test_case = db.relationship('TestCase')
    
    __table_args__ = (
        db.Index('idx_template_id', 'template_id'),
        db.Index('idx_site_scope_id', 'site_scope_id'),
        db.Index('idx_sync_status', 'sync_status'),
    )

class RequirementMapping(db.Model):
    """Track requirement inheritance and customization across scopes"""
    __tablename__ = 'requirement_mappings'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    scope_id = db.Column(db.String(36), db.ForeignKey('validation_scopes.id'), nullable=False)
    global_requirement_id = db.Column(db.String(36), nullable=False)  # Reference to global requirement
    site_requirement_id = db.Column(db.String(36), db.ForeignKey('requirements.id'), nullable=True)
    
    # Mapping status
    is_inherited = db.Column(db.Boolean, default=True)
    is_customized = db.Column(db.Boolean, default=False)
    customization_notes = db.Column(db.Text)
    
    # Traceability
    global_test_coverage = db.Column(db.Integer, default=0)  # How many global tests cover this
    site_test_coverage = db.Column(db.Integer, default=0)  # How many site tests cover this
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    scope = db.relationship('ValidationScope')
    site_requirement = db.relationship('Requirement')
    
    __table_args__ = (
        db.Index('idx_scope_id_mapping', 'scope_id'),
        db.Index('idx_global_req_id', 'global_requirement_id'),
        db.Index('idx_is_customized', 'is_customized'),
    )

class ScopeChangeLog(db.Model):
    """Track all changes to scope configurations for audit trail"""
    __tablename__ = 'scope_change_logs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    scope_id = db.Column(db.String(36), db.ForeignKey('validation_scopes.id'), nullable=False)
    
    change_type = db.Column(db.String(50), nullable=False)  # INHERIT, CUSTOMIZE, OVERRIDE, LOCK, UNLOCK
    entity_type = db.Column(db.String(50), nullable=False)  # TEST, REQUIREMENT, RISK
    entity_id = db.Column(db.String(36), nullable=False)
    
    old_value = db.Column(db.JSON)  # Before state
    new_value = db.Column(db.JSON)  # After state
    change_reason = db.Column(db.Text)
    
    changed_by = db.Column(db.String(36), db.ForeignKey('users.id'))
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    scope = db.relationship('ValidationScope', backref='change_logs')
    user = db.relationship('User')
    
    __table_args__ = (
        db.Index('idx_scope_id_log', 'scope_id'),
        db.Index('idx_change_type', 'change_type'),
        db.Index('idx_changed_at', 'changed_at'),
    )
