from alembic import op
import sqlalchemy as sa
from datetime import datetime

def upgrade():
    op.create_table('validation_protocols',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('protocol_name', sa.String(255), nullable=False),
        sa.Column('phase', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), default='PLANNED'),
        sa.Column('scope', sa.Text, nullable=False),
        sa.Column('acceptance_criteria', sa.Text, nullable=False),
        sa.Column('created_by_id', sa.Integer, sa.ForeignKey('user.id'), nullable=False),
        sa.Column('created_at', sa.DateTime, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow),
        sa.Column('approved_by_id', sa.Integer, sa.ForeignKey('user.id')),
        sa.Column('approved_at', sa.DateTime),
        sa.Index('idx_validation_protocols_phase', 'phase'),
        sa.Index('idx_validation_protocols_status', 'status')
    )
    
    op.create_table('validation_results',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('protocol_id', sa.Integer, sa.ForeignKey('validation_protocols.id'), nullable=False),
        sa.Column('test_case', sa.String(255), nullable=False),
        sa.Column('expected_outcome', sa.Text, nullable=False),
        sa.Column('actual_outcome', sa.Text, nullable=False),
        sa.Column('passed', sa.Boolean, nullable=False),
        sa.Column('evidence_location', sa.String(500)),
        sa.Column('executed_by_id', sa.Integer, sa.ForeignKey('user.id'), nullable=False),
        sa.Column('executed_at', sa.DateTime, default=datetime.utcnow),
        sa.Column('reviewed_by_id', sa.Integer, sa.ForeignKey('user.id')),
        sa.Column('reviewed_at', sa.DateTime),
        sa.Index('idx_validation_results_protocol', 'protocol_id'),
        sa.Index('idx_validation_results_passed', 'passed')
    )
    
    op.create_table('comprehensive_audit_logs',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('audit_type', sa.String(100), nullable=False),
        sa.Column('entity_type', sa.String(100), nullable=False),
        sa.Column('entity_id', sa.Integer, nullable=False),
        sa.Column('action', sa.String(255), nullable=False),
        sa.Column('old_values', sa.Text),
        sa.Column('new_values', sa.Text),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('user.id'), nullable=False),
        sa.Column('timestamp', sa.DateTime, default=datetime.utcnow, index=True),
        sa.Column('ip_address', sa.String(45)),
        sa.Column('user_agent', sa.String(500)),
        sa.Column('checksum', sa.String(256), nullable=False, index=True),
        sa.Column('created_at', sa.DateTime, default=datetime.utcnow),
        sa.Index('idx_comprehensive_audit_type', 'audit_type'),
        sa.Index('idx_comprehensive_audit_entity', 'entity_type')
    )
    
    op.create_table('system_health_metrics',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('metric_name', sa.String(255), nullable=False),
        sa.Column('metric_value', sa.Float, nullable=False),
        sa.Column('threshold_min', sa.Float),
        sa.Column('threshold_max', sa.Float),
        sa.Column('status', sa.String(50), default='OK'),
        sa.Column('recorded_at', sa.DateTime, default=datetime.utcnow, index=True),
        sa.Column('created_at', sa.DateTime, default=datetime.utcnow),
        sa.Index('idx_system_health_name', 'metric_name'),
        sa.Index('idx_system_health_status', 'status')
    )

def downgrade():
    op.drop_index('idx_system_health_status')
    op.drop_index('idx_system_health_name')
    op.drop_table('system_health_metrics')
    op.drop_index('idx_comprehensive_audit_entity')
    op.drop_index('idx_comprehensive_audit_type')
    op.drop_table('comprehensive_audit_logs')
    op.drop_index('idx_validation_results_passed')
    op.drop_index('idx_validation_results_protocol')
    op.drop_table('validation_results')
    op.drop_index('idx_validation_protocols_status')
    op.drop_index('idx_validation_protocols_phase')
    op.drop_table('validation_protocols')
