import re
import hashlib
import secrets
from datetime import datetime, timedelta
from app.models.auth_access_control import (
    UserPasswordPolicy, UserPasswordHistory, AccessLog, UserSession,
    SegregationOfDutiesRule, FailedLoginAttempt, PasswordPolicyLevel, MFAType, SessionStatus
)
from app.models.user import User, UserRole
from app import db
import pyotp

class AccessControlService:
    MIN_PASSWORD_LENGTH = 12
    PASSWORD_COMPLEXITY_PATTERN = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{12,}$'
    SESSION_TIMEOUT_MINUTES = 15
    
    @staticmethod
    def validate_password_policy(password, policy):
        errors = []
        if len(password) < policy.min_length:
            errors.append(f"Password must be at least {policy.min_length} characters")
        if policy.require_uppercase and not re.search(r'[A-Z]', password):
            errors.append("Password must contain uppercase letters")
        if policy.require_lowercase and not re.search(r'[a-z]', password):
            errors.append("Password must contain lowercase letters")
        if policy.require_numbers and not re.search(r'\d', password):
            errors.append("Password must contain numbers")
        if policy.require_special_chars and not re.search(r'[@$!%*?&]', password):
            errors.append("Password must contain special characters")
        return errors
    
    @staticmethod
    def check_password_history(user_id, new_password, policy):
        past_passwords = UserPasswordHistory.query.filter(
            UserPasswordHistory.user_id == user_id
        ).order_by(UserPasswordHistory.set_at.desc()).limit(policy.history_count).all()
        
        new_hash = hashlib.sha256(new_password.encode()).hexdigest()
        for hist in past_passwords:
            if hist.password_hash == new_hash:
                return False
        return True
    
    @staticmethod
    def set_password(user_id, password):
        policy = UserPasswordPolicy.query.filter_by(user_id=user_id).first()
        if not policy:
            policy = UserPasswordPolicy(user_id=user_id, created_by_id=user_id)
            db.session.add(policy)
        
        errors = AccessControlService.validate_password_policy(password, policy)
        if errors:
            return False, errors
        
        if not AccessControlService.check_password_history(user_id, password, policy):
            return False, ["Password was recently used. Please choose a different password."]
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        history = UserPasswordHistory(user_id=user_id, password_hash=password_hash)
        db.session.add(history)
        db.session.commit()
        return True, ["Password set successfully"]
    
    @staticmethod
    def setup_mfa(user_id, mfa_type=MFAType.TOTP):
        policy = UserPasswordPolicy.query.filter_by(user_id=user_id).first()
        if not policy:
            return None, "User policy not found"
        
        if mfa_type == MFAType.TOTP:
            secret = pyotp.random_base32()
            policy.mfa_secret = secret
            policy.mfa_type = MFAType.TOTP
            db.session.commit()
            totp = pyotp.TOTP(secret)
            return totp.provisioning_uri(name=f'Westval:{user_id}', issuer_name='Westval'), secret
        return None, "MFA type not supported"
    
    @staticmethod
    def verify_mfa(user_id, token):
        policy = UserPasswordPolicy.query.filter_by(user_id=user_id).first()
        if not policy or not policy.mfa_secret:
            return False
        
        totp = pyotp.TOTP(policy.mfa_secret)
        return totp.verify(token, valid_window=1)
    
    @staticmethod
    def create_session(user_id, ip_address, user_agent, mfa_verified=False):
        token = secrets.token_urlsafe(64)
        session = UserSession(
            user_id=user_id,
            token=token,
            ip_address=ip_address,
            user_agent=user_agent,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=8),
            status=SessionStatus.ACTIVE,
            mfa_verified=mfa_verified
        )
        db.session.add(session)
        db.session.commit()
        return session
    
    @staticmethod
    def validate_session(token):
        session = UserSession.query.filter_by(token=token).first()
        if not session:
            return None
        if session.status != SessionStatus.ACTIVE:
            return None
        if datetime.utcnow() > session.expires_at:
            session.status = SessionStatus.EXPIRED
            db.session.commit()
            return None
        if (datetime.utcnow() - session.last_activity).total_seconds() > (AccessControlService.SESSION_TIMEOUT_MINUTES * 60):
            session.status = SessionStatus.TIMEOUT
            db.session.commit()
            return None
        session.last_activity = datetime.utcnow()
        db.session.commit()
        return session
    
    @staticmethod
    def log_access(user_id, action, resource_type, ip_address, status, resource_id=None, session_id=None, details=None):
        log = AccessLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            status=status,
            session_id=session_id,
            details=details
        )
        db.session.add(log)
        db.session.commit()
        return log
    
    @staticmethod
    def check_segregation_of_duties(user_id, action_type, resource_type):
        user = User.query.get(user_id)
        if not user:
            return True
        
        user_roles = [ur.role_name for ur in user.user_roles]
        
        conflicting_rules = SegregationOfDutiesRule.query.filter(
            SegregationOfDutiesRule.is_active == True,
            SegregationOfDutiesRule.action_type == action_type,
            SegregationOfDutiesRule.resource_type == resource_type
        ).all()
        
        for rule in conflicting_rules:
            if rule.role_1 in user_roles and rule.role_2 in user_roles:
                return False
        return True
    
    @staticmethod
    def record_failed_login(user_id, ip_address):
        attempt = FailedLoginAttempt.query.filter_by(user_id=user_id, ip_address=ip_address).first()
        if not attempt:
            attempt = FailedLoginAttempt(user_id=user_id, ip_address=ip_address)
        attempt.attempt_count += 1
        attempt.last_attempt = datetime.utcnow()
        
        policy = UserPasswordPolicy.query.filter_by(user_id=user_id).first()
        if policy and attempt.attempt_count >= policy.failed_attempt_lockout:
            attempt.locked_until = datetime.utcnow() + timedelta(minutes=policy.lockout_duration_minutes)
            attempt.reason = "Account locked due to failed login attempts"
        
        db.session.add(attempt)
        db.session.commit()
        return attempt
    
    @staticmethod
    def check_account_lockout(user_id, ip_address):
        attempt = FailedLoginAttempt.query.filter_by(user_id=user_id, ip_address=ip_address).first()
        if not attempt:
            return False, 0
        if attempt.locked_until and datetime.utcnow() < attempt.locked_until:
            return True, (attempt.locked_until - datetime.utcnow()).total_seconds() / 60
        return False, 0
    
    @staticmethod
    def reset_failed_login(user_id, ip_address):
        attempt = FailedLoginAttempt.query.filter_by(user_id=user_id, ip_address=ip_address).first()
        if attempt:
            db.session.delete(attempt)
            db.session.commit()
