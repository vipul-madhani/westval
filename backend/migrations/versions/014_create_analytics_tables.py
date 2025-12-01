from alembic import op
import sqlalchemy as sa
revision='014'
down_revision='013'
def upgrade():
Sprint 11: Database Migration for Analytics    op.create_table('widget',sa.Column('id',sa.Integer,primary_key=True),sa.Column('dashboard_id',sa.Integer,sa.ForeignKey('dashboard.id')),sa.Column('widget_type',sa.String(50)),sa.Column('position',sa.Integer),sa.Column('config',sa.JSON),sa.Column('created_at',sa.DateTime))
    op.create_table('metric',sa.Column('id',sa.Integer,primary_key=True),sa.Column('project_id',sa.Integer,sa.ForeignKey('project.id')),sa.Column('metric_name',sa.String(100)),sa.Column('metric_value',sa.Float),sa.Column('metric_type',sa.String(50)),sa.Column('timestamp',sa.DateTime))
    op.create_table('report',sa.Column('id',sa.Integer,primary_key=True),sa.Column('project_id',sa.Integer,sa.ForeignKey('project.id')),sa.Column('report_type',sa.String(100)),sa.Column('data',sa.JSON),sa.Column('generated_at',sa.DateTime),sa.Column('generated_by',sa.Integer,sa.ForeignKey('user.id')))
    op.create_index('ix_metric_project_id','metric',['project_id'])
    op.create_index('ix_dashboard_user_id','dashboard',['user_id'])
def downgrade():
    op.drop_index('ix_dashboard_user_id')
    op.drop_index('ix_metric_project_id')
    op.drop_table('report')
    op.drop_table('metric')
    op.drop_table('widget')
    op.drop_table('dashboard')
