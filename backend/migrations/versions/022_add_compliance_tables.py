from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table('compliance_docs', sa.Column('id', sa.Integer(), pk=True), sa.Column('doc_type', sa.String(50)), sa.Column('title', sa.String(255)), sa.Column('content', sa.Text()), sa.Column('requirement_id', sa.Integer(), sa.FK('requirements.id')), sa.Column('status', sa.String(20), server_default='DRAFT'), sa.Column('created_by_id', sa.Integer(), sa.FK('users.id')), sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()), sa.Index('idx_comp_docs_status', 'status'))
    op.create_table('req_traceability', sa.Column('id', sa.Integer(), pk=True), sa.Column('requirement_id', sa.Integer(), sa.FK('requirements.id')), sa.Column('doc_id', sa.Integer(), sa.FK('compliance_docs.id')), sa.Column('test_id', sa.Integer()), sa.Column('status', sa.String(20), server_default='PENDING'), sa.Column('traced_at', sa.DateTime(), server_default=sa.func.now()))
    op.create_table('compliance_trails', sa.Column('id', sa.Integer(), pk=True), sa.Column('doc_id', sa.Integer(), sa.FK('compliance_docs.id')), sa.Column('action', sa.String(100)), sa.Column('changed_by_id', sa.Integer(), sa.FK('users.id')), sa.Column('timestamp', sa.DateTime(), server_default=sa.func.now()), sa.Column('details', sa.Text()))

def downgrade():
    op.drop_table('compliance_trails')
    op.drop_table('req_traceability')
    op.drop_table('compliance_docs')
