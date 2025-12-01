"""Create test management tables

Revision ID: 005_create_test_mgmt
Revises: 004
Create Date: 2024-01-15 10:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision = '005_create_test_mgmt'
down_revision = '004'
branch_labels = None
depends_on = None

def upgrade():
    # Create test_plans table
    op.create_table(
        'test_plans',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('validation_id', sa.String(36), nullable=False),
        sa.Column('project_id', sa.String(36), nullable=False),
        sa.Column('created_by', sa.String(36), nullable=False),
        sa.Column('status', sa.String(20), default='DRAFT'),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['validation_id'], ['validations.id']),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.Index('idx_validation_id', 'validation_id')
    )
    
    # Create test_sets table
    op.create_table(
        'test_sets',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('test_plan_id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('scope', sa.String(50), default='FUNCTIONAL'),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.ForeignKeyConstraint(['test_plan_id'], ['test_plans.id'], ondelete='CASCADE'),
        sa.Index('idx_test_plan_id', 'test_plan_id')
    )
    
    # Create test_cases table
    op.create_table(
        'test_cases',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('test_set_id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('requirement_id', sa.String(36), nullable=True),
        sa.Column('status', sa.String(20), default='ACTIVE'),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.ForeignKeyConstraint(['test_set_id'], ['test_sets.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['requirement_id'], ['requirements.id']),
        sa.Index('idx_test_set_id', 'test_set_id'),
        sa.Index('idx_requirement_id', 'requirement_id')
    )
    
    # Create test_steps table
    op.create_table(
        'test_steps',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('test_case_id', sa.String(36), nullable=False),
        sa.Column('step_number', sa.Integer, nullable=False),
        sa.Column('action', sa.Text, nullable=False),
        sa.Column('expected_result', sa.Text, nullable=False),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.ForeignKeyConstraint(['test_case_id'], ['test_cases.id'], ondelete='CASCADE'),
        sa.Index('idx_test_case_id', 'test_case_id')
    )
    
    # Create test_executions table
    op.create_table(
        'test_executions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('test_case_id', sa.String(36), nullable=False),
        sa.Column('execution_date', sa.DateTime, nullable=False),
        sa.Column('executed_by', sa.String(36), nullable=False),
        sa.Column('total_steps', sa.Integer, default=0),
        sa.Column('passed_steps', sa.Integer, default=0),
        sa.Column('failed_steps', sa.Integer, default=0),
        sa.Column('overall_status', sa.String(20), default='IN_PROGRESS'),
        sa.Column('comments', sa.Text, nullable=True),
        sa.Column('defect_linked', sa.Boolean, default=False),
        sa.Column('defect_ids', mysql.JSON, default={}),
        sa.ForeignKeyConstraint(['test_case_id'], ['test_cases.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['executed_by'], ['users.id']),
        sa.Index('idx_test_case_id_exec', 'test_case_id'),
        sa.Index('idx_execution_date', 'execution_date')
    )
    
    # Create test_step_results table
    op.create_table(
        'test_step_results',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('execution_id', sa.String(36), nullable=False),
        sa.Column('step_id', sa.String(36), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('actual_result', sa.Text, nullable=False),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('screenshot_urls', mysql.JSON, default=[]),
        sa.Column('duration_seconds', sa.Integer, default=0),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.ForeignKeyConstraint(['execution_id'], ['test_executions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['step_id'], ['test_steps.id']),
        sa.Index('idx_execution_id', 'execution_id'),
        sa.Index('idx_step_id', 'step_id')
    )

def downgrade():
    op.drop_table('test_step_results')
    op.drop_table('test_executions')
    op.drop_table('test_steps')
    op.drop_table('test_cases')
    op.drop_table('test_sets')
    op.drop_table('test_plans')
