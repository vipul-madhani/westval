"""Authentication service with 21 CFR Part 11 compliance"""
from datetime import datetime, timedelta
from app import db
from app.models.user import User
from app.models.audit import AuditLog
import hashlib
import secrets

class AuthService:
    @staticmethod
    def create_user(data, created_by_id=None):
        """Create new user with audit trail"""
        user = User(
            email=data['email'],
            username=data.get('username', data['email'].split('@')[0]),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            department=data.get('department'),
            job_title=data.get('job_title'),
            phone=data.get('phone')
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.flush()
        
        # Create audit log
        audit = AuditLog(
            user_id=created_by_id or user.id,
            user_name=f"{user.first_name} {user.last_name}",
            action='CREATE',
            entity_type='User',
            entity_id=user.id,
            entity_name=user.email,
            change_description=f'User account created: {user.email}',
            timestamp=datetime.utcnow()
        )
        db.session.add(audit)
        db.session.commit()
        
        return user
    
    @staticmethod
    def authenticate(email, password, ip_address=None, device_info=None):
        """Authenticate user and create audit log"""
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            # Log failed attempt
            if user:
                audit = AuditLog(
                    user_id=user.id,
                    user_name=user.email,
                    action='LOGIN_FAILED',
                    entity_type='User',
                    entity_id=user.id,
                    entity_name=user.email,
                    change_description='Failed login attempt',
                    timestamp=datetime.utcnow(),
                    ip_address=ip_address,
                    device_info=device_info
                )
                db.session.add(audit)
                db.session.commit()
            return None
        
        if not user.is_active:
            return None
        
        # Update last login
        user.last_login = datetime.utcnow()
        
        # Log successful login
        audit = AuditLog(
            user_id=user.id,
            user_name=f"{user.first_name} {user.last_name}",
            action='LOGIN_SUCCESS',
            entity_type='User',
            entity_id=user.id,
            entity_name=user.email,
            change_description='Successful login',
            timestamp=datetime.utcnow(),
            ip_address=ip_address,
            device_info=device_info
        )
        db.session.add(audit)
        db.session.commit()
        
        return user
    
    @staticmethod
    def validate_password_strength(password):
        """Validate password meets CFR Part 11 requirements"""
        errors = []
        
        if len(password) < 12:
            errors.append('Password must be at least 12 characters long')
        
        if not any(c.isupper() for c in password):
            errors.append('Password must contain at least one uppercase letter')
        
        if not any(c.islower() for c in password):
            errors.append('Password must contain at least one lowercase letter')
        
        if not any(c.isdigit() for c in password):
            errors.append('Password must contain at least one number')
        
        if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            errors.append('Password must contain at least one special character')
        
        return len(errors) == 0, errors