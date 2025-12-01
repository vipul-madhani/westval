"""Add Digital Signature tables for 21 CFR Part 11 compliance

Revision ID: 016
Revises: 015
Create Date: 2024-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision = '016'
down_revision = '015'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('digital_certificates',
        sa.Column('id', sa.String(128), nullable=False),
        sa.Column('certificate_pem', sa.Text(), nullable=False),
        sa.Column('public_key_pem', sa.Text(), nullable=False),
        sa.Column('private_key_pem', sa.Text(), nullable=True),
        sa.Column('subject_dn', sa.String(512), nullable=False),
        sa.Column('issuer_dn', sa.String(512), nullable=False),
        sa.Column('serial_number', sa.String(128), nullable=False, unique=True),
        sa.Column('issued_date', sa.DateTime(), nullable=False),
        sa.Column('expiry_date', sa.DateTime(), nullable=False),
        sa.Column('thumbprint', sa.String(128), nullable=False, unique=True),
        sa.Column('algorithm', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, default='VALID'),
        sa.Column('is_ca', sa.Boolean(), default=False),
        sa.Column('key_length', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(128), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('created_by_id', sa.String(128), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=sa.func.current_timestamp(), onupdate=sa.func.current_timestamp()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_digital_certificates_serial_number', 'digital_certificates', ['serial_number'])
    op.create_index('ix_digital_certificates_thumbprint', 'digital_certificates', ['thumbprint'])
    op.create_index('ix_digital_certificates_status', 'digital_certificates', ['status'])
    op.create_index('ix_digital_certificates_user_id', 'digital_certificates', ['user_id'])

    op.create_table('digital_signatures',
        sa.Column('id', sa.String(128), nullable=False),
        sa.Column('document_id', sa.String(128), sa.ForeignKey('documents.id'), nullable=False),
        sa.Column('document_type', sa.String(50), nullable=False),
        sa.Column('signature_value', sa.Text(), nullable=False),
        sa.Column('signature_hash', sa.String(256), nullable=False, unique=True),
        sa.Column('certificate_id', sa.String(128), sa.ForeignKey('digital_certificates.id'), nullable=False),
        sa.Column('signed_by_id', sa.String(128), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('signature_timestamp', sa.DateTime(), nullable=False),
        sa.Column('tsa_timestamp', sa.DateTime(), nullable=True),
        sa.Column('tsa_token', sa.Text(), nullable=True),
        sa.Column('algorithm', sa.String(50), nullable=False),
        sa.Column('is_valid', sa.Boolean(), default=True),
        sa.Column('validation_timestamp', sa.DateTime(), nullable=True),
        sa.Column('validation_details', sa.Text(), nullable=True),
        sa.Column('reason', sa.String(512), nullable=True),
        sa.Column('location', sa.String(256), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=sa.func.current_timestamp(), onupdate=sa.func.current_timestamp()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_digital_signatures_document_id', 'digital_signatures', ['document_id'])
    op.create_index('ix_digital_signatures_certificate_id', 'digital_signatures', ['certificate_id'])
    op.create_index('ix_digital_signatures_signed_by_id', 'digital_signatures', ['signed_by_id'])
    op.create_index('ix_digital_signatures_is_valid', 'digital_signatures', ['is_valid'])

    op.create_table('signature_revocations',
        sa.Column('id', sa.String(128), nullable=False),
        sa.Column('certificate_id', sa.String(128), sa.ForeignKey('digital_certificates.id'), nullable=False),
        sa.Column('revoked_at', sa.DateTime(), nullable=False),
        sa.Column('revoked_by_id', sa.String(128), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('reason', sa.String(512), nullable=False),
        sa.Column('crl_entry_number', sa.Integer(), nullable=False),
        sa.Column('revocation_timestamp', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=sa.func.current_timestamp(), onupdate=sa.func.current_timestamp()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_signature_revocations_certificate_id', 'signature_revocations', ['certificate_id'])
    op.create_index('ix_signature_revocations_revoked_by_id', 'signature_revocations', ['revoked_by_id'])

def downgrade():
    op.drop_index('ix_signature_revocations_revoked_by_id', table_name='signature_revocations')
    op.drop_index('ix_signature_revocations_certificate_id', table_name='signature_revocations')
    op.drop_table('signature_revocations')
    op.drop_index('ix_digital_signatures_is_valid', table_name='digital_signatures')
    op.drop_index('ix_digital_signatures_signed_by_id', table_name='digital_signatures')
    op.drop_index('ix_digital_signatures_certificate_id', table_name='digital_signatures')
    op.drop_index('ix_digital_signatures_document_id', table_name='digital_signatures')
    op.drop_table('digital_signatures')
    op.drop_index('ix_digital_certificates_user_id', table_name='digital_certificates')
    op.drop_index('ix_digital_certificates_status', table_name='digital_certificates')
    op.drop_index('ix_digital_certificates_thumbprint', table_name='digital_certificates')
    op.drop_index('ix_digital_certificates_serial_number', table_name='digital_certificates')
    op.drop_table('digital_certificates')
