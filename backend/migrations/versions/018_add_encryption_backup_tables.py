from alembic import op
import sqlalchemy as sa
from datetime import datetime

def upgrade():
    op.create_table('encryption_keys',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('key_identifier', sa.String(255), unique=True, nullable=False),
        sa.Column('algorithm', sa.String(50), nullable=False),
        sa.Column('key_material', sa.Text, nullable=False),
        sa.Column('key_version', sa.Integer, default=1),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_by_id', sa.Integer, sa.ForeignKey('user.id'), nullable=False),
        sa.Column('created_at', sa.DateTime, default=datetime.utcnow),
        sa.Column('rotation_date', sa.DateTime),
        sa.Index('idx_encryption_keys_active', 'is_active'),
        sa.Index('idx_encryption_keys_created', 'created_by_id')
    )
    
    op.create_table('data_encryptions',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('plaintext_hash', sa.String(256), nullable=False),
        sa.Column('ciphertext', sa.Text, nullable=False),
        sa.Column('nonce', sa.String(255), nullable=False),
        sa.Column('tag', sa.String(255), nullable=False),
        sa.Column('algorithm', sa.String(50), nullable=False),
        sa.Column('key_id', sa.Integer, sa.ForeignKey('encryption_keys.id'), nullable=False),
        sa.Column('created_by_id', sa.Integer, sa.ForeignKey('user.id'), nullable=False),
        sa.Column('created_at', sa.DateTime, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow),
        sa.Index('idx_data_encryptions_key', 'key_id'),
        sa.Index('idx_data_encryptions_created', 'created_by_id')
    )
    
    op.create_table('backup_records',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('backup_name', sa.String(255), nullable=False),
        sa.Column('backup_location', sa.String(100), nullable=False),
        sa.Column('backup_path', sa.Text, nullable=False),
        sa.Column('backup_checksum', sa.String(256), nullable=False),
        sa.Column('status', sa.String(50), default='PENDING'),
        sa.Column('compressed', sa.Boolean, default=False),
        sa.Column('encryption_key_id', sa.Integer, sa.ForeignKey('encryption_keys.id')),
        sa.Column('created_by_id', sa.Integer, sa.ForeignKey('user.id'), nullable=False),
        sa.Column('created_at', sa.DateTime, default=datetime.utcnow),
        sa.Column('backup_date', sa.DateTime),
        sa.Index('idx_backup_records_status', 'status'),
        sa.Index('idx_backup_records_created', 'created_by_id')
    )
    
    op.create_table('backup_integrity_logs',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('backup_id', sa.Integer, sa.ForeignKey('backup_records.id'), nullable=False),
        sa.Column('checksum_expected', sa.String(256), nullable=False),
        sa.Column('checksum_actual', sa.String(256), nullable=False),
        sa.Column('integrity_verified', sa.Boolean, default=False),
        sa.Column('files_checked', sa.Integer, default=0),
        sa.Column('files_corrupted', sa.Integer, default=0),
        sa.Column('recovery_possible', sa.Boolean, default=True),
        sa.Column('verified_by_id', sa.Integer, sa.ForeignKey('user.id')),
        sa.Column('verification_timestamp', sa.DateTime, default=datetime.utcnow),
        sa.Index('idx_backup_integrity_backup', 'backup_id'),
        sa.Index('idx_backup_integrity_verified', 'integrity_verified')
    )

def downgrade():
    op.drop_index('idx_backup_integrity_verified')
    op.drop_index('idx_backup_integrity_backup')
    op.drop_table('backup_integrity_logs')
    op.drop_index('idx_backup_records_created')
    op.drop_index('idx_backup_records_status')
    op.drop_table('backup_records')
    op.drop_index('idx_data_encryptions_created')
    op.drop_index('idx_data_encryptions_key')
    op.drop_table('data_encryptions')
    op.drop_index('idx_encryption_keys_created')
    op.drop_index('idx_encryption_keys_active')
    op.drop_table('encryption_keys')
