"""Initial database schema

Revision ID: 001
Revises: 
Create Date: 2025-12-02
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('username', sa.String(100), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('first_name', sa.String(100)),
        sa.Column('last_name', sa.String(100)),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('is_admin', sa.Boolean, default=False),
        sa.Column('department', sa.String(100)),
        sa.Column('job_title', sa.String(100)),
        sa.Column('phone', sa.String(20)),
        sa.Column('signature_meaning', sa.Text),
        sa.Column('signature_certified', sa.Boolean, default=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),
        sa.Column('last_login', sa.DateTime)
    )
    
    # Roles table
    op.create_table(
        'roles',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(50), unique=True, nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('permissions', sa.JSON),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now())
    )
    
    # User roles mapping
    op.create_table(
        'user_roles',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('role_id', sa.String(36), sa.ForeignKey('roles.id'), nullable=False),
        sa.Column('assigned_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('assigned_by', sa.String(36), sa.ForeignKey('users.id'))
    )
    
    # Validation projects
    op.create_table(
        'validation_projects',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('project_number', sa.String(50), unique=True, nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('validation_type', sa.String(50)),
        sa.Column('methodology', sa.String(50)),
        sa.Column('gamp_category', sa.String(10)),
        sa.Column('risk_level', sa.String(20)),
        sa.Column('risk_score', sa.Integer),
        sa.Column('status', sa.String(50), default='Planning'),
        sa.Column('owner_id', sa.String(36), sa.ForeignKey('users.id')),
        sa.Column('department', sa.String(100)),
        sa.Column('planned_start_date', sa.Date),
        sa.Column('planned_end_date', sa.Date),
        sa.Column('actual_start_date', sa.Date),
        sa.Column('actual_end_date', sa.Date),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),
        sa.Column('created_by', sa.String(36), sa.ForeignKey('users.id'))
    )
    
    # Audit logs
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('user_name', sa.String(255), nullable=False),
        sa.Column('user_role', sa.String(100)),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('entity_type', sa.String(100), nullable=False),
        sa.Column('entity_id', sa.String(36), nullable=False),
        sa.Column('entity_name', sa.String(255)),
        sa.Column('field_changed', sa.String(100)),
        sa.Column('old_value', sa.Text),
        sa.Column('new_value', sa.Text),
        sa.Column('change_description', sa.Text),
        sa.Column('reason', sa.Text),
        sa.Column('timestamp', sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column('ip_address', sa.String(45)),
        sa.Column('device_info', sa.String(255)),
        sa.Column('browser_info', sa.String(255)),
        sa.Column('session_id', sa.String(100)),
        sa.Column('request_id', sa.String(100)),
        sa.Column('checksum', sa.String(255))
    )
    
    op.create_index('idx_audit_timestamp', 'audit_logs', ['timestamp'])
    op.create_index('idx_audit_entity', 'audit_logs', ['entity_type', 'entity_id'])

def downgrade():
    op.drop_index('idx_audit_entity')
    op.drop_index('idx_audit_timestamp')
    op.drop_table('audit_logs')
    op.drop_table('validation_projects')
    op.drop_table('user_roles')
    op.drop_table('roles')
    op.drop_table('users')