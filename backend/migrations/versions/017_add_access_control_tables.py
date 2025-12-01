"""Add Access Control tables for password policies, MFA, sessions, SoD enforcement

Revision ID: 017
Revises: 016
Create Date: 2024-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision = '017'
down_revision = '016'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('user_password_policies',
        sa.Column('id', sa.String(128), nullable=False),
        sa.Column('user_id', sa.String(128), sa.ForeignKey('users.id'), nullable=False, unique=True),
        sa.Column('min_length', sa.Integer(), default=12),
        sa.Column('require_uppercase', sa.Boolean(), default=True),
        sa.Column('require_lowercase', sa.Boolean(), default=True),
        sa.Column('require_numbers', sa.Boolean(), default=True),
        sa.Column('require_special_chars', sa.Boolean(), default=True),
        sa.Column('max_age_days', sa.Integer(), default=90),
        sa.Column('min_age_days', sa.Integer(), default=1),
        sa.Column('history_count', sa.Integer(), default=5),
        sa.Column('failed_attempt_lockout', sa.Integer(), default=5),
        sa.Column('lockout_duration_minutes', sa.Integer(), default=30),
        sa.Column('policy_level', sa.String(50), default='FDA_COMPLIANT'),
        sa.Column('last_policy_change', sa.DateTime(), nullable=False, default=sa.func.current_timestamp()),
        sa.Column('mfa_enabled', sa.Boolean(), default=True),
        sa.Column('mfa_type', sa.String(50), default='TOTP'),
        sa.Column('mfa_secret', sa.String(255), nullable=True),
        sa.Column('created_by_id', sa.String(128), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=sa.func.current_timestamp(), onupdate=sa.func.current_timestamp()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_user_password_policies_user_id', 'user_password_policies', ['user_id'])

    op.create_table('user_password_history',
        sa.Column('id', sa.String(128), nullable=False),
        sa.Column('user_id', sa.String(128), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('set_at', sa.DateTime(), nullable=False, default=sa.func.current_timestamp()),
        sa.Column('expired_at', sa.DateTime(), nullable=True),
        sa.Column('reason', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=sa.func.current_timestamp(), onupdate=sa.func.current_timestamp()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_user_password_history_user_id', 'user_password_history', ['user_id'])
    op.create_index('ix_user_password_history_set_at', 'user_password_history', ['set_at'])

    op.create_table('user_sessions',
        sa.Column('id', sa.String(128), nullable=False),
        sa.Column('user_id', sa.String(128), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('token', sa.String(512), nullable=False, unique=True),
        sa.Column('ip_address', sa.String(45), nullable=False),
        sa.Column('user_agent', sa.String(512), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.current_timestamp()),
        sa.Column('last_activity', sa.DateTime(), nullable=False, default=sa.func.current_timestamp()),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('status', sa.String(50), default='ACTIVE'),
        sa.Column('mfa_verified', sa.Boolean(), default=False),
        sa.Column('device_fingerprint', sa.String(256), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=sa.func.current_timestamp(), onupdate=sa.func.current_timestamp()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_user_sessions_user_id', 'user_sessions', ['user_id'])
    op.create_index('ix_user_sessions_token', 'user_sessions', ['token'])
    op.create_index('ix_user_sessions_status', 'user_sessions', ['status'])
    op.create_index('ix_user_sessions_expires_at', 'user_sessions', ['expires_at'])

    op.create_table('access_logs',
        sa.Column('id', sa.String(128), nullable=False),
        sa.Column('user_id', sa.String(128), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('resource_type', sa.String(50), nullable=False),
        sa.Column('resource_id', sa.String(128), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=False),
        sa.Column('user_agent', sa.String(512), nullable=True),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False, default=sa.func.current_timestamp()),
        sa.Column('session_id', sa.String(128), sa.ForeignKey('user_sessions.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=sa.func.current_timestamp(), onupdate=sa.func.current_timestamp()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_access_logs_user_id', 'access_logs', ['user_id'])
    op.create_index('ix_access_logs_timestamp', 'access_logs', ['timestamp'])
    op.create_index('ix_access_logs_action', 'access_logs', ['action'])
    op.create_index('ix_access_logs_status', 'access_logs', ['status'])

    op.create_table('segregation_of_duties_rules',
        sa.Column('id', sa.String(128), nullable=False),
        sa.Column('name', sa.String(128), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('role_1', sa.String(128), nullable=False),
        sa.Column('role_2', sa.String(128), nullable=False),
        sa.Column('action_type', sa.String(100), nullable=False),
        sa.Column('resource_type', sa.String(50), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_by_id', sa.String(128), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=sa.func.current_timestamp(), onupdate=sa.func.current_timestamp()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_segregation_of_duties_rules_is_active', 'segregation_of_duties_rules', ['is_active'])
    op.create_index('ix_segregation_of_duties_rules_roles', 'segregation_of_duties_rules', ['role_1', 'role_2'])

    op.create_table('failed_login_attempts',
        sa.Column('id', sa.String(128), nullable=False),
        sa.Column('user_id', sa.String(128), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('attempt_count', sa.Integer(), default=1),
        sa.Column('last_attempt', sa.DateTime(), nullable=False, default=sa.func.current_timestamp()),
        sa.Column('ip_address', sa.String(45), nullable=False),
        sa.Column('locked_until', sa.DateTime(), nullable=True),
        sa.Column('reason', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=sa.func.current_timestamp(), onupdate=sa.func.current_timestamp()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_failed_login_attempts_user_id', 'failed_login_attempts', ['user_id'])
    op.create_index('ix_failed_login_attempts_ip_address', 'failed_login_attempts', ['ip_address'])
    op.create_index('ix_failed_login_attempts_locked_until', 'failed_login_attempts', ['locked_until'])

def downgrade():
    op.drop_index('ix_failed_login_attempts_locked_until', table_name='failed_login_attempts')
    op.drop_index('ix_failed_login_attempts_ip_address', table_name='failed_login_attempts')
    op.drop_index('ix_failed_login_attempts_user_id', table_name='failed_login_attempts')
    op.drop_table('failed_login_attempts')
    op.drop_index('ix_segregation_of_duties_rules_roles', table_name='segregation_of_duties_rules')
    op.drop_index('ix_segregation_of_duties_rules_is_active', table_name='segregation_of_duties_rules')
    op.drop_table('segregation_of_duties_rules')
    op.drop_index('ix_access_logs_status', table_name='access_logs')
    op.drop_index('ix_access_logs_action', table_name='access_logs')
    op.drop_index('ix_access_logs_timestamp', table_name='access_logs')
    op.drop_index('ix_access_logs_user_id', table_name='access_logs')
    op.drop_table('access_logs')
    op.drop_index('ix_user_sessions_expires_at', table_name='user_sessions')
    op.drop_index('ix_user_sessions_status', table_name='user_sessions')
    op.drop_index('ix_user_sessions_token', table_name='user_sessions')
    op.drop_index('ix_user_sessions_user_id', table_name='user_sessions')
    op.drop_table('user_sessions')
    op.drop_index('ix_user_password_history_set_at', table_name='user_password_history')
    op.drop_index('ix_user_password_history_user_id', table_name='user_password_history')
    op.drop_table('user_password_history')
    op.drop_index('ix_user_password_policies_user_id', table_name='user_password_policies')
    op.drop_table('user_password_policies')
