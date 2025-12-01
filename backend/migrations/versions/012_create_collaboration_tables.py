from alembic import op
import sqlalchemy as sa

revision = '012'
down_revision = '011'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'threaded_comment',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('user.id'), nullable=False),
        sa.Column('document_id', sa.Integer, sa.ForeignKey('document.id'), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('content_hash', sa.String(64), nullable=False),
        sa.Column('parent_comment_id', sa.Integer, sa.ForeignKey('threaded_comment.id'), nullable=True),
        sa.Column('is_resolved', sa.Boolean, default=False),
        sa.Column('resolved_by_id', sa.Integer, sa.ForeignKey('user.id'), nullable=True),
        sa.Column('resolved_at', sa.DateTime, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=True)
    )
    op.create_index('ix_threaded_comment_document_id', 'threaded_comment', ['document_id'])
    op.create_index('ix_threaded_comment_parent_id', 'threaded_comment', ['parent_comment_id'])
    
    op.create_table(
        'notification',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('user.id'), nullable=False),
        sa.Column('notification_type', sa.String(50), nullable=False),
        sa.Column('source_id', sa.Integer, nullable=False),
        sa.Column('message', sa.Text, nullable=False),
        sa.Column('is_read', sa.Boolean, default=False),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('read_at', sa.DateTime, nullable=True)
    )
    op.create_index('ix_notification_user_id', 'notification', ['user_id'])
    op.create_index('ix_notification_is_read', 'notification', ['is_read'])

def downgrade():
    op.drop_index('ix_notification_is_read')
    op.drop_index('ix_notification_user_id')
    op.drop_table('notification')
    op.drop_index('ix_threaded_comment_parent_id')
    op.drop_index('ix_threaded_comment_document_id')
    op.drop_table('threaded_comment')
