from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table('admin_users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('user.id'), unique=True, nullable=False),
        sa.Column('is_super_admin', sa.Boolean, default=False),
        sa.Column('department', sa.String(100)),
        sa.Column('created_at', sa.DateTime, index=True)
    )
    op.create_table('user_roles',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('role_name', sa.String(100), unique=True, nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('is_system_role', sa.Boolean, default=False),
        sa.Column('created_at', sa.DateTime)
    )
    op.create_table('role_permissions',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('role_id', sa.Integer, sa.ForeignKey('user_roles.id'), nullable=False),
        sa.Column('permission_type', sa.String(50), nullable=False),
        sa.Column('resource_name', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime, index=True)
    )
    op.create_table('user_permissions',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('admin_user_id', sa.Integer, sa.ForeignKey('admin_users.id'), nullable=False),
        sa.Column('permission_type', sa.String(50), nullable=False),
        sa.Column('resource_name', sa.String(255), nullable=False),
        sa.Column('granted_by_id', sa.Integer, sa.ForeignKey('user.id')),
        sa.Column('created_at', sa.DateTime, index=True)
    )
    op.create_table('system_config',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('config_key', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('config_value', sa.Text, nullable=False),
        sa.Column('data_type', sa.String(50)),
        sa.Column('description', sa.Text),
        sa.Column('is_encrypted', sa.Boolean, default=False),
        sa.Column('updated_by_id', sa.Integer, sa.ForeignKey('user.id')),
        sa.Column('updated_at', sa.DateTime)
    )
    op.create_table('audit_settings',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('setting_name', sa.String(255), unique=True, nullable=False),
        sa.Column('enabled', sa.Boolean, default=True),
        sa.Column('config', sa.JSON),
        sa.Column('created_at', sa.DateTime)
    )

def downgrade():
    op.drop_table('audit_settings')
    op.drop_table('system_config')
    op.drop_table('user_permissions')
    op.drop_table('role_permissions')
    op.drop_table('user_roles')
    op.drop_table('admin_users')
