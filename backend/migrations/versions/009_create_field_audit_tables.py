"""Create field audit trail tables.

Revision ID: 009
Revises: 008
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers
revision = '009'
down_revision = '008'
branch_labels = None
depends_on = None

def upgrade():
    # field_audit_logs table
    op.create_table(
        'field_audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('entity_type', sa.String(length=100), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.Column('field_name', sa.String(length=255), nullable=False),
        sa.Column('old_value', sa.Text(), nullable=True),
        sa.Column('new_value', sa.Text(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('change_timestamp', sa.DateTime(), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('change_reason', sa.Text(), nullable=True),
        sa.Column('approval_status', sa.String(length=50), nullable=False),
        sa.Column('approved_by', sa.Integer(), nullable=True),
        sa.Column('approval_timestamp', sa.DateTime(), nullable=True),
        sa.Column('change_hash', sa.String(length=256), nullable=False),
        sa.Column('previous_hash', sa.String(length=256), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.ForeignKeyConstraint(['approved_by'], ['user.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('change_hash')
    )
    op.create_index('idx_entity', 'field_audit_logs', ['entity_type', 'entity_id'])
    op.create_index('idx_user_timestamp', 'field_audit_logs', ['user_id', 'change_timestamp'])
    op.create_index('idx_field_change', 'field_audit_logs', ['field_name', 'change_timestamp'])
    
    # change_requests table
    op.create_table(
        'change_requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('change_number', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('change_type', sa.String(length=50), nullable=False),
        sa.Column('priority', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('requested_by', sa.Integer(), nullable=False),
        sa.Column('assigned_to', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('submitted_at', sa.DateTime(), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('implemented_at', sa.DateTime(), nullable=True),
        sa.Column('impact_assessment', sa.JSON(), nullable=True),
        sa.Column('implementation_plan', sa.JSON(), nullable=True),
        sa.Column('external_change_id', sa.String(length=100), nullable=True),
        sa.Column('external_source', sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(['requested_by'], ['user.id']),
        sa.ForeignKeyConstraint(['assigned_to'], ['user.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('change_number')
    )
    op.create_index('idx_status_created', 'change_requests', ['status', 'created_at'])
    op.create_index('idx_external_id', 'change_requests', ['external_change_id'])
    
    # document_comments table
    op.create_table(
        'document_comments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('entity_type', sa.String(length=100), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.Column('parent_comment_id', sa.Integer(), nullable=True),
        sa.Column('comment_text', sa.Text(), nullable=False),
        sa.Column('comment_author_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_resolved', sa.Boolean(), nullable=False),
        sa.Column('resolution_notes', sa.Text(), nullable=True),
        sa.Column('resolved_by', sa.Integer(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('attachments', sa.JSON(), nullable=True),
        sa.Column('mentions', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['comment_author_id'], ['user.id']),
        sa.ForeignKeyConstraint(['parent_comment_id'], ['document_comments.id']),
        sa.ForeignKeyConstraint(['resolved_by'], ['user.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_entity_comment', 'document_comments', ['entity_type', 'entity_id', 'created_at'])
    op.create_index('idx_thread', 'document_comments', ['parent_comment_id'])
    
    # risk_assessments table
    op.create_table(
        'risk_assessments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('risk_id', sa.String(length=50), nullable=False),
        sa.Column('validation_id', sa.Integer(), nullable=False),
        sa.Column('risk_description', sa.Text(), nullable=False),
        sa.Column('risk_category', sa.String(length=100), nullable=False),
        sa.Column('severity', sa.Integer(), nullable=False),
        sa.Column('probability', sa.Integer(), nullable=False),
        sa.Column('risk_priority_number', sa.Integer(), nullable=False),
        sa.Column('current_controls', sa.JSON(), nullable=True),
        sa.Column('mitigation_actions', sa.JSON(), nullable=True),
        sa.Column('residual_risk', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['validation_id'], ['validation.id']),
        sa.ForeignKeyConstraint(['owner_id'], ['user.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('risk_id')
    )
    op.create_index('idx_validation_risk', 'risk_assessments', ['validation_id', 'status'])
    op.create_index('idx_risk_priority', 'risk_assessments', ['risk_priority_number'])

def downgrade():
    op.drop_index('idx_risk_priority', 'risk_assessments')
    op.drop_index('idx_validation_risk', 'risk_assessments')
    op.drop_table('risk_assessments')
    op.drop_index('idx_thread', 'document_comments')
    op.drop_index('idx_entity_comment', 'document_comments')
    op.drop_table('document_comments')
    op.drop_index('idx_external_id', 'change_requests')
    op.drop_index('idx_status_created', 'change_requests')
    op.drop_table('change_requests')
    op.drop_index('idx_field_change', 'field_audit_logs')
    op.drop_index('idx_user_timestamp', 'field_audit_logs')
    op.drop_index('idx_entity', 'field_audit_logs')
    op.drop_table('field_audit_logs')
