from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from . import db

class PermissionType(enum.Enum):
    READ = 'READ'
    CREATE = 'CREATE'
    UPDATE = 'UPDATE'
    DELETE = 'DELETE'
    APPROVE = 'APPROVE'
    ADMIN = 'ADMIN'

class AdminUser(db.Model):
    __tablename__ = 'admin_users'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, unique=True)
    is_super_admin = Column(Boolean, default=False)
    department = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    permissions = relationship('UserPermission', backref='admin_user')

class UserRole(db.Model):
    __tablename__ = 'user_roles'
    id = Column(Integer, primary_key=True)
    role_name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    is_system_role = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    permissions = relationship('RolePermission', backref='role')

class RolePermission(db.Model):
    __tablename__ = 'role_permissions'
    id = Column(Integer, primary_key=True)
    role_id = Column(Integer, ForeignKey('user_roles.id'), nullable=False)
    permission_type = Column(Enum(PermissionType), nullable=False)
    resource_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

class UserPermission(db.Model):
    __tablename__ = 'user_permissions'
    id = Column(Integer, primary_key=True)
    admin_user_id = Column(Integer, ForeignKey('admin_users.id'), nullable=False)
    permission_type = Column(Enum(PermissionType), nullable=False)
    resource_name = Column(String(255), nullable=False)
    granted_by_id = Column(Integer, ForeignKey('user.id'))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

class SystemConfig(db.Model):
    __tablename__ = 'system_config'
    id = Column(Integer, primary_key=True)
    config_key = Column(String(255), unique=True, nullable=False, index=True)
    config_value = Column(Text, nullable=False)
    data_type = Column(String(50))
    description = Column(Text)
    is_encrypted = Column(Boolean, default=False)
    updated_by_id = Column(Integer, ForeignKey('user.id'))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AuditSetting(db.Model):
    __tablename__ = 'audit_settings'
    id = Column(Integer, primary_key=True)
    setting_name = Column(String(255), unique=True, nullable=False)
    enabled = Column(Boolean, default=True)
    config = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
