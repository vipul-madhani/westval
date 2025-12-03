"""User model for authentication and authorization"""
from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    is_locked = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_ldap_user = db.Column(db.Boolean, default=False)
    failed_login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime, nullable=True)
    department = db.Column(db.String(100))
    job_title = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    
    # 21 CFR Part 11 compliance fields
    signature_meaning = db.Column(db.Text)  # Meaning of electronic signature
    signature_certified = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    roles = db.relationship('UserRole', back_populates='user', foreign_keys='UserRole.user_id', cascade='all, delete-orphan')
    audit_logs = db.relationship('AuditLog', back_populates='user')
    signatures = db.relationship('ElectronicSignature', back_populates='user')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Serialize user object"""
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'department': self.department,
            'job_title': self.job_title,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'roles': [role.role.name for role in self.roles]
        }

class Role(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    permissions = db.Column(db.JSON)  # Array of permission strings
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    users = db.relationship('UserRole', back_populates='role')

class UserRole(db.Model):
    __tablename__ = 'user_roles'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    role_id = db.Column(db.String(36), db.ForeignKey('roles.id'), nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    assigned_by = db.Column(db.String(36), db.ForeignKey('users.id'))
    
    user = db.relationship('User', back_populates='roles', foreign_keys=[user_id])
    role = db.relationship('Role', back_populates='users', foreign_keys=[role_id])