"""Create global vs site validation tables

Revision ID: 006_global_site
Revises: 005_create_test_mgmt
Create Date: 2024-01-15 11:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision = '006_global_site'
down_revision = '005_create_test_mgmt'
branch_labels = None
depends_on = None

def upgrade():
    # Create validation_scopes table
    op.create_table(
        'validation_scopes',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('validation_id', sa.String(36), sa.ForeignKey('validations.id'), nullable=False),
        sa.Column('scope_type', sa.String(20), nullable=False),
        sa.Column('scope_name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('parent_scope_id', sa.String(36), sa.ForeignKey('validation_scopes.id')),
        sa.Column('inherit_requirements', sa.Boolean, default=True),
        sa.Column('inherit_tests', sa.Boolean, default=True),
        sa.Column('inherit_risks', sa.Boolean, default=True),
        sa.Column('customizations', mysql.JSON, default={}),
        sa.Column('is_locked', sa.Boolean, default=False),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', sa.String(36), sa.ForeignKey('users.id')),
        sa.Index('idx_validation_id_scope', 'validation_id'),
        sa.Index('idx_scope_type', 'scope_type')
    )
    
    # Create test_templates table
    op.create_table(
        'test_templates',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('scope_id', sa.String(36), sa.ForeignKey('validation_scopes.id'), nullable=False),
        sa.Column('parent_template_id', sa.String(36), sa.ForeignKey('test_templates.id')),
        sa.Column('test_case_id', sa.String(36), sa.ForeignKey('test_cases.id')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('is_global_template', sa.Boolean, default=False),
        sa.Column('is_inherited', sa.Boolean, default=False),
        sa.Column('customization_allowed', sa.Boolean, default=True),
        sa.Column('customizations', mysql.JSON, default={}),
        sa.Column('override_fields', mysql.JSON, default={}),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now()),
        sa.Index('idx_scope_id_template', 'scope_id'),
        sa.Index('idx_is_global_template', 'is_global_template')
    )
    
    # Create test_site_instances table
    op.create_table(
        'test_site_instances',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('template_id', sa.String(36), sa.ForeignKey('test_templates.id'), nullable=False),
        sa.Column('site_scope_id', sa.String(36), sa.ForeignKey('validation_scopes.id'), nullable=False),
        sa.Column('test_case_id', sa.String(36), sa.ForeignKey('test_cases.id')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('customizations', mysql.JSON, default={}),
        sa.Column('overrides', mysql.JSON, default={}),
        sa.Column('sync_status', sa.String(20), default='SYNCED'),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now()),
        sa.Index('idx_template_id_instance', 'template_id'),
        sa.Index('idx_site_scope_id', 'site_scope_id'),
        sa.Index('idx_sync_status', 'sync_status')
    )
    
    # Create requirement_mappings table
    op.create_table(
        'requirement_mappings',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('scope_id', sa.String(36), sa.ForeignKey('validation_scopes.id'), nullable=False),
        sa.Column('global_requirement_id', sa.String(36), nullable=False),
        sa.Column('site_requirement_id', sa.String(36), sa.ForeignKey('requirements.id')),
        sa.Column('is_inherited', sa.Boolean, default=True),
        sa.Column('is_customized', sa.Boolean, default=False),
        sa.Column('customization_notes', sa.Text),
        sa.Column('global_test_coverage', sa.Integer, default=0),
        sa.Column('site_test_coverage', sa.Integer, default=0),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now()),
        sa.Index('idx_scope_id_mapping', 'scope_id'),
        sa.Index('idx_global_req_id', 'global_requirement_id'),
        sa.Index('idx_is_customized_mapping', 'is_customized')
    )
    
    # Create scope_change_logs table
    op.create_table(
        'scope_change_logs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('scope_id', sa.String(36), sa.ForeignKey('validation_scopes.id'), nullable=False),
        sa.Column('change_type', sa.String(50), nullable=False),
        sa.Column('entity_type', sa.String(50), nullable=False),
        sa.Column('entity_id', sa.String(36), nullable=False),
        sa.Column('old_value', mysql.JSON),
        sa.Column('new_value', mysql.JSON),
        sa.Column('change_reason', sa.Text),
        sa.Column('changed_by', sa.String(36), sa.ForeignKey('users.id')),
        sa.Column('changed_at', sa.DateTime, default=sa.func.now()),
        sa.Index('idx_scope_id_log', 'scope_id'),
        sa.Index('idx_change_type', 'change_type'),
        sa.Index('idx_changed_at', 'changed_at')
    )

def downgrade():
    op.drop_table('scope_change_logs')
    op.drop_table('requirement_mappings')
    op.drop_table('test_site_instances')
    op.drop_table('test_templates')
    op.drop_table('validation_scopes')
