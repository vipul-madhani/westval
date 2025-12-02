from ..models.admin_panel import AdminUser, UserRole, RolePermission, UserPermission, SystemConfig, PermissionType
from sqlalchemy import db
from datetime import datetime

class AdminPanelService:
    @staticmethod
    def create_role(role_name, description, permissions):
        role = UserRole(role_name=role_name, description=description)
        db.session.add(role)
        db.session.commit()
        for perm in permissions:
            rp = RolePermission(role_id=role.id, permission_type=perm['type'], resource_name=perm['resource'])
            db.session.add(rp)
        db.session.commit()
        return role
    
    @staticmethod
    def assign_permission(admin_user_id, permission_type, resource_name, granted_by_id):
        perm = UserPermission(admin_user_id=admin_user_id, permission_type=permission_type, resource_name=resource_name, granted_by_id=granted_by_id)
        db.session.add(perm)
        db.session.commit()
        return perm
    
    @staticmethod
    def set_system_config(key, value, data_type='string', encrypted=False, updated_by_id=None):
        config = SystemConfig.query.filter_by(config_key=key).first()
        if not config:
            config = SystemConfig(config_key=key, config_value=value, data_type=data_type, is_encrypted=encrypted, updated_by_id=updated_by_id)
            db.session.add(config)
        else:
            config.config_value = value
            config.updated_at = datetime.utcnow()
            config.updated_by_id = updated_by_id
        db.session.commit()
        return config
    
    @staticmethod
    def get_system_config(key):
        return SystemConfig.query.filter_by(config_key=key).first()
    
    @staticmethod
    def check_permission(user_id, resource_name, permission_type):
        perm = UserPermission.query.filter_by(admin_user_id=user_id, resource_name=resource_name, permission_type=permission_type).first()
        return perm is not None
