"""Create AI Automation & DMS Tables

Revision ID: 008_create_ai_dms_tables
Revises: 007_create_reports_tables
Create Date: 2025-12-02
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from datetime import datetime

revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade():
    # Create qms_documents table
    op.create_table(
        'qms_documents',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('document_name', sa.String(255), nullable=False),
        sa.Column('document_type', sa.Enum('SOP', 'Work Instruction', 'Form', 'Template', 'Policy'), nullable=False),
        sa.Column('document_content', sa.LargeBinary(), nullable=False),
        sa.Column('file_format', sa.String(50), nullable=False),
        sa.Column('file_size_bytes', sa.Integer(), nullable=False),
        sa.Column('content_hash', sa.String(128), nullable=False, index=True),
        sa.Column('version', sa.Integer(), nullable=False, default=1),
        sa.Column('upload_date', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column('uploaded_by_user_id', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('compliance_status', sa.Enum('Draft', 'Under Review', 'Approved', 'Obsolete'), default='Draft'),
        sa.ForeignKeyConstraint(['uploaded_by_user_id'], ['users.id']),
        sa.Index('idx_qms_doc_hash', 'content_hash'),
        sa.Index('idx_qms_doc_type', 'document_type'),
        sa.Index('idx_qms_doc_active', 'is_active')
    )

    # Create ai_extractions table
    op.create_table(
        'ai_extractions',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('qms_document_id', sa.Integer(), nullable=False),
        sa.Column('extraction_type', sa.Enum('Requirements', 'Processes', 'Risks', 'Controls', 'Test Cases'), nullable=False),
        sa.Column('extracted_data', sa.JSON(), nullable=False),
        sa.Column('ai_model_used', sa.String(100), nullable=False, default='GPT-4'),
        sa.Column('extraction_confidence', sa.Float(), nullable=False),
        sa.Column('tokens_used', sa.Integer(), nullable=False),
        sa.Column('extraction_timestamp', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column('extracted_by_user_id', sa.Integer(), nullable=False),
        sa.Column('quality_score', sa.Float(), nullable=False),
        sa.Column('manual_review_status', sa.Enum('Pending', 'Reviewed', 'Approved', 'Rejected'), default='Pending'),
        sa.Column('review_comments', sa.Text()),
        sa.ForeignKeyConstraint(['qms_document_id'], ['qms_documents.id']),
        sa.ForeignKeyConstraint(['extracted_by_user_id'], ['users.id']),
        sa.Index('idx_ai_extract_qms', 'qms_document_id'),
        sa.Index('idx_ai_extract_type', 'extraction_type'),
        sa.Index('idx_ai_extract_confidence', 'extraction_confidence')
    )

    # Create requirement_extractions table
    op.create_table(
        'requirement_extractions',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('ai_extraction_id', sa.Integer(), nullable=False),
        sa.Column('requirement_text', sa.Text(), nullable=False),
        sa.Column('requirement_category', sa.Enum('Functional', 'Performance', 'Security', 'Compliance', 'Operational'), nullable=False),
        sa.Column('priority_level', sa.Enum('Critical', 'High', 'Medium', 'Low'), nullable=False),
        sa.Column('traceability_id', sa.String(100), nullable=False, index=True),
        sa.Column('source_section', sa.String(255), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=False),
        sa.Column('validation_status', sa.Enum('Draft', 'Under Review', 'Approved', 'Implemented'), default='Draft'),
        sa.Column('associated_test_cases', sa.JSON()),
        sa.Column('created_date', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column('created_by_user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['ai_extraction_id'], ['ai_extractions.id']),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id']),
        sa.Index('idx_req_extract_ai', 'ai_extraction_id'),
        sa.Index('idx_req_extract_category', 'requirement_category'),
        sa.Index('idx_req_extract_traceability', 'traceability_id')
    )

    # Create ai_templates table
    op.create_table(
        'ai_templates',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('template_name', sa.String(255), nullable=False),
        sa.Column('template_type', sa.Enum('Validation Plan', 'Test Plan', 'Risk Assessment', 'Summary Report'), nullable=False),
        sa.Column('source_extraction_ids', sa.JSON(), nullable=False),
        sa.Column('generated_content', sa.LongText(), nullable=False),
        sa.Column('template_version', sa.Integer(), nullable=False, default=1),
        sa.Column('generation_timestamp', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column('generated_by_user_id', sa.Integer(), nullable=False),
        sa.Column('approval_status', sa.Enum('Draft', 'Submitted for Approval', 'Approved', 'Rejected'), default='Draft'),
        sa.Column('approved_by_user_id', sa.Integer()),
        sa.Column('approval_date', sa.DateTime()),
        sa.Column('approval_comments', sa.Text()),
        sa.Column('document_format', sa.Enum('PDF', 'DOCX', 'HTML', 'JSON'), nullable=False, default='PDF'),
        sa.Column('metadata', sa.JSON()),
        sa.Column('is_locked', sa.Boolean(), default=False),
        sa.ForeignKeyConstraint(['generated_by_user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['approved_by_user_id'], ['users.id']),
        sa.Index('idx_ai_template_type', 'template_type'),
        sa.Index('idx_ai_template_status', 'approval_status')
    )

    # Create dms_documents table
    op.create_table(
        'dms_documents',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('ai_template_id', sa.Integer(), nullable=False),
        sa.Column('dms_document_id', sa.String(100), nullable=False, unique=True, index=True),
        sa.Column('dms_repository_name', sa.String(100), nullable=False),
        sa.Column('migration_timestamp', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column('migrated_by_user_id', sa.Integer(), nullable=False),
        sa.Column('source_qms_document_id', sa.Integer(), nullable=False),
        sa.Column('traceability_chain', sa.JSON(), nullable=False),
        sa.Column('migration_status', sa.Enum('Pending', 'In Progress', 'Completed', 'Failed'), default='Pending'),
        sa.Column('validation_status', sa.Enum('Not Validated', 'Validated', 'Failed Validation'), default='Not Validated'),
        sa.Column('audit_trail', sa.JSON(), nullable=False),
        sa.Column('digital_signature', sa.String(255)),
        sa.Column('signature_timestamp', sa.DateTime()),
        sa.Column('cfr_21_compliant', sa.Boolean(), default=False),
        sa.Column('is_archived', sa.Boolean(), default=False),
        sa.ForeignKeyConstraint(['ai_template_id'], ['ai_templates.id']),
        sa.ForeignKeyConstraint(['migrated_by_user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['source_qms_document_id'], ['qms_documents.id']),
        sa.Index('idx_dms_doc_id', 'dms_document_id'),
        sa.Index('idx_dms_doc_status', 'migration_status'),
        sa.Index('idx_dms_doc_compliance', 'cfr_21_compliant')
    )

    # Create indexes on critical columns
    op.create_index('idx_qms_documents_version', 'qms_documents', ['version'])
    op.create_index('idx_ai_extractions_timestamp', 'ai_extractions', ['extraction_timestamp'])
    op.create_index('idx_requirement_priority', 'requirement_extractions', ['priority_level'])
    op.create_index('idx_ai_templates_generated', 'ai_templates', ['generation_timestamp'])
    op.create_index('idx_dms_traceability', 'dms_documents', ['source_qms_document_id'])


def downgrade():
    op.drop_index('idx_dms_traceability', 'dms_documents')
    op.drop_index('idx_ai_templates_generated', 'ai_templates')
    op.drop_index('idx_requirement_priority', 'requirement_extractions')
    op.drop_index('idx_ai_extractions_timestamp', 'ai_extractions')
    op.drop_index('idx_qms_documents_version', 'qms_documents')
    
    op.drop_table('dms_documents')
    op.drop_table('ai_templates')
    op.drop_table('requirement_extractions')
    op.drop_table('ai_extractions')
    op.drop_table('qms_documents')
