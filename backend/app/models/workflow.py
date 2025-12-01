"""Advanced Workflow Engine for Pharma Validation

Phase 2: Complete workflow state machine with:
- Dynamic workflow templates
- Role-based transition rules
- Parallel approval signatures
- Conditional business logic
- Automated actions on state transitions
- Dynamic form configuration per state
- Comprehensive audit trail with cryptographic integrity

Compliant with 21 CFR Part 11 and EU Annex 11
"""

from datetime import datetime, timedelta
from sqlalchemy.dialects.mysql import JSON
from app import db
import uuid


# =============================================================================
# WORKFLOW TEMPLATE & STATE DEFINITIONS
# =============================================================================

class WorkflowTemplate(db.Model):
    """Enterprise-grade workflow templates for validation projects"""
    __tablename__ = 'workflow_templates'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False, unique=True)
    description = db.Column(db.Text)
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    states = db.relationship('WorkflowState', backref='template', cascade='all, delete-orphan')
    transitions = db.relationship('WorkflowTransition', backref='template', cascade='all, delete-orphan')
    rules = db.relationship('WorkflowRule', backref='template', cascade='all, delete-orphan')
    form_configs = db.relationship('DynamicFormConfig', backref='template', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<WorkflowTemplate {self.name}>'


class WorkflowState(db.Model):
    """Workflow states (Draft, Review, Execution, Approved, etc.)"""
    __tablename__ = 'workflow_states'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    template_id = db.Column(db.String(36), db.ForeignKey('workflow_templates.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    order = db.Column(db.Integer, nullable=False)  # Sequence in workflow
    color = db.Column(db.String(7), default='#3498db')  # UI visualization
    is_initial = db.Column(db.Boolean, default=False)  # Starting state
    is_final = db.Column(db.Boolean, default=False)  # Terminal state
    requires_signature = db.Column(db.Boolean, default=False)
    sla_hours = db.Column(db.Integer)  # SLA for this state
    metadata = db.Column(JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    outgoing_transitions = db.relationship('WorkflowTransition', foreign_keys='WorkflowTransition.from_state_id', backref='from_state')
    incoming_transitions = db.relationship('WorkflowTransition', foreign_keys='WorkflowTransition.to_state_id', backref='to_state')
    document_states = db.relationship('DocumentWorkflowState', backref='state')
    
    __table_args__ = (db.UniqueConstraint('template_id', 'name', name='uq_template_state_name'),)
    
    def __repr__(self):
        return f'<WorkflowState {self.name}>'


# =============================================================================
# WORKFLOW TRANSITIONS & RULES
# =============================================================================

class WorkflowTransition(db.Model):
    """Allowed transitions between states"""
    __tablename__ = 'workflow_transitions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    template_id = db.Column(db.String(36), db.ForeignKey('workflow_templates.id'), nullable=False)
    from_state_id = db.Column(db.String(36), db.ForeignKey('workflow_states.id'), nullable=False)
    to_state_id = db.Column(db.String(36), db.ForeignKey('workflow_states.id'), nullable=False)
    name = db.Column(db.String(255))  # "Approve", "Reject", "Return for Revision"
    requires_comment = db.Column(db.Boolean, default=False)
    auto_assign_to_role = db.Column(db.String(255))  # Auto-assign to role when entered
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    rules = db.relationship('WorkflowRule', backref='transition', cascade='all, delete-orphan')
    actions = db.relationship('WorkflowAction', backref='transition', cascade='all, delete-orphan')
    
    __table_args__ = (db.UniqueConstraint('template_id', 'from_state_id', 'to_state_id', name='uq_transition'),)
    
    def __repr__(self):
        return f'<WorkflowTransition {self.name}>'


class WorkflowRule(db.Model):
    """Gating conditions: roles, parallel approvals, business logic"""
    __tablename__ = 'workflow_rules'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    template_id = db.Column(db.String(36), db.ForeignKey('workflow_templates.id'), nullable=False)
    transition_id = db.Column(db.String(36), db.ForeignKey('workflow_transitions.id'), nullable=False)
    
    # Rule types: 'role_required', 'parallel_approval', 'condition_check', 'no_deviations'
    rule_type = db.Column(db.String(50), nullable=False)
    
    # Role-based access
    required_role = db.Column(db.String(255))
    
    # Parallel approval signatures
    requires_signatures = db.Column(db.Integer, default=1)
    signature_roles = db.Column(JSON)  # [{role: 'QA Manager', required: true}, ...]
    
    # Conditional logic
    condition_field = db.Column(db.String(255))
    condition_operator = db.Column(db.String(50))  # 'equals', 'not_empty', 'greater_than'
    condition_value = db.Column(db.String(255))
    
    is_blocking = db.Column(db.Boolean, default=True)  # Blocks transition if fails
    description = db.Column(db.Text)
    metadata = db.Column(JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<WorkflowRule {self.rule_type}>'


class WorkflowAction(db.Model):
    """Automated actions triggered on transition"""
    __tablename__ = 'workflow_actions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    transition_id = db.Column(db.String(36), db.ForeignKey('workflow_transitions.id'), nullable=False)
    
    # Action types: 'lock_fields', 'unlock_fields', 'send_notification', 'create_task'
    action_type = db.Column(db.String(50), nullable=False)
    parameters = db.Column(JSON)  # Action config
    order = db.Column(db.Integer, default=0)  # Execution order
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<WorkflowAction {self.action_type}>'


# =============================================================================
# DYNAMIC FORM CONFIGURATION
# =============================================================================

class DynamicFormConfig(db.Model):
    """Custom fields for each workflow state"""
    __tablename__ = 'dynamic_form_configs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    template_id = db.Column(db.String(36), db.ForeignKey('workflow_templates.id'), nullable=False)
    state_id = db.Column(db.String(36), db.ForeignKey('workflow_states.id'), nullable=False)
    
    field_name = db.Column(db.String(255), nullable=False)
    field_type = db.Column(db.String(50), nullable=False)  # text, date, dropdown, file, signature
    label = db.Column(db.String(255), nullable=False)
    placeholder = db.Column(db.String(255))
    is_required = db.Column(db.Boolean, default=False)
    order = db.Column(db.Integer, default=0)
    
    # Conditional visibility
    conditional_field = db.Column(db.String(255))
    conditional_value = db.Column(db.String(255))
    
    options = db.Column(JSON)  # For dropdowns
    validation_rules = db.Column(JSON)  # {min_length, max_length, pattern}
    metadata = db.Column(JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('template_id', 'state_id', 'field_name', name='uq_form_field'),)
    
    def __repr__(self):
        return f'<DynamicFormConfig {self.field_name}>'


# =============================================================================
# DOCUMENT WORKFLOW STATE TRACKING
# =============================================================================

class DocumentWorkflowState(db.Model):
    """Tracks document position in workflow + parallel approvals"""
    __tablename__ = 'document_workflow_states'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = db.Column(db.String(36), db.ForeignKey('validation_documents.id'), nullable=False)
    current_state_id = db.Column(db.String(36), db.ForeignKey('workflow_states.id'), nullable=False)
    previous_state_id = db.Column(db.String(36), db.ForeignKey('workflow_states.id'))
    
    assigned_to = db.Column(db.String(36), db.ForeignKey('users.id'))  # Current owner
    moved_by = db.Column(db.String(36), db.ForeignKey('users.id'))  # Who initiated transition
    transition_reason = db.Column(db.Text)
    
    entered_at = db.Column(db.DateTime, default=datetime.utcnow)
    sla_deadline = db.Column(db.DateTime)  # SLA expiration
    
    # Parallel approval tracking
    required_approvals = db.Column(db.Integer, default=0)
    completed_approvals = db.Column(db.Integer, default=0)
    approvals_data = db.Column(JSON)  # [{user_id, role, timestamp, signature, signed_by}, ...]
    
    is_locked = db.Column(db.Boolean, default=False)
    metadata = db.Column(JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    document = db.relationship('ValidationDocument', backref='workflow_states')
    current_state = db.relationship('WorkflowState', foreign_keys=[current_state_id])
    
    def __repr__(self):
        return f'<DocumentWorkflowState {self.document_id}>'


class WorkflowAuditLog(db.Model):
    """Immutable audit trail - 21 CFR Part 11 compliant"""
    __tablename__ = 'workflow_audit_logs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = db.Column(db.String(36), db.ForeignKey('validation_documents.id'), nullable=False)
    
    action = db.Column(db.String(100), nullable=False)  # state_change, approval_given, etc.
    from_state = db.Column(db.String(255))
    to_state = db.Column(db.String(255))
    
    performed_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Cryptographic integrity
    data_hash = db.Column(db.String(512))  # SHA-256 hash
    signature = db.Column(db.Text)  # Digital signature
    
    details = db.Column(JSON)  # Additional metadata
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    
    def __repr__(self):
        return f'<WorkflowAuditLog {self.action}>'
