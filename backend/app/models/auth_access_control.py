from datetime import datetime, timedelta
from enum import Enum
from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, Enum as SQLEnum, ForeignKey, JSON
from app import db
from app.models.base_model import BaseModel
import json

class PasswordPolicyLevel(Enum):
    BASIC = "BASIC"
    STANDARD = "STANDARD"
    ENHANCED = "ENHANCED"
    FDA_COMPLIANT = "FDA_COMPLIANT"

class MFAType(Enum):
    TOTP = "TOTP"
    SMS = "SMS"
    EMAIL = "EMAIL"
    HARDWARE_KEY = "HARDWARE_KEY"

class SessionStatus(Enum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"
    TIMEOUT = "TIMEOUT"

class UserPasswordPolicy(BaseModel):
    __tablename__ = 'user_password_policies'
    user_id = Column(String(128), ForeignKey('users.id'), nullable=False, unique=True)
    min_length = Column(Integer, default=12, nullable=False)
    require_uppercase = Column(Boolean, default=True)
    require_lowercase = Column(Boolean, default=True)
    require_numbers = Column(Boolean, default=True)
    require_special_chars = Column(Boolean, default=True)
    max_age_days = Column(Integer, default=90, nullable=False)
    min_age_days = Column(Integer, default=1, nullable=False)
    history_count = Column(Integer, default=5, nullable=False)
    failed_attempt_lockout = Column(Integer, default=5, nullable=False)
    lockout_duration_minutes = Column(Integer, default=30, nullable=False)
    policy_level = Column(SQLEnum(PasswordPolicyLevel), default=PasswordPolicyLevel.FDA_COMPLIANT)
    last_policy_change = Column(DateTime, nullable=False, default=datetime.utcnow)
    mfa_enabled = Column(Boolean, default=True)
    mfa_type = Column(SQLEnum(MFAType), default=MFAType.TOTP)
    mfa_secret = Column(String(255), nullable=True)
    created_by_id = Column(String(128), ForeignKey('users.id'), nullable=False)

class UserPasswordHistory(BaseModel):
    __tablename__ = 'user_password_history'
    user_id = Column(String(128), ForeignKey('users.id'), nullable=False)
    password_hash = Column(String(255), nullable=False)
    set_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    expired_at = Column(DateTime, nullable=True)
    reason = Column(String(100), nullable=True)

class AccessLog(BaseModel):
    __tablename__ = 'access_logs'
    user_id = Column(String(128), ForeignKey('users.id'), nullable=False)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(String(128), nullable=True)
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(String(512), nullable=True)
    status = Column(String(20), nullable=False)
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    session_id = Column(String(128), ForeignKey('user_sessions.id'), nullable=True)

class UserSession(BaseModel):
    __tablename__ = 'user_sessions'
    user_id = Column(String(128), ForeignKey('users.id'), nullable=False)
    token = Column(String(512), nullable=False, unique=True)
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(String(512), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_activity = Column(DateTime, nullable=False, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    status = Column(SQLEnum(SessionStatus), default=SessionStatus.ACTIVE)
    mfa_verified = Column(Boolean, default=False)
    device_fingerprint = Column(String(256), nullable=True)

class SegregationOfDutiesRule(BaseModel):
    __tablename__ = 'segregation_of_duties_rules'
    name = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)
    role_1 = Column(String(128), nullable=False)
    role_2 = Column(String(128), nullable=False)
    action_type = Column(String(100), nullable=False)
    resource_type = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True)
    created_by_id = Column(String(128), ForeignKey('users.id'), nullable=False)
    reason = Column(Text, nullable=True)

class FailedLoginAttempt(BaseModel):
    __tablename__ = 'failed_login_attempts'
    user_id = Column(String(128), ForeignKey('users.id'), nullable=False)
    attempt_count = Column(Integer, default=1, nullable=False)
    last_attempt = Column(DateTime, nullable=False, default=datetime.utcnow)
    ip_address = Column(String(45), nullable=False)
    locked_until = Column(DateTime, nullable=True)
    reason = Column(String(255), nullable=True)
