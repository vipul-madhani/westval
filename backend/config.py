"""Application configuration management"""
import os
from datetime import timedelta

class Config:
    """Base configuration"""
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = False
    TESTING = False
    
    # Database - MySQL Support
    DB_TYPE = os.getenv('DB_TYPE', 'mysql')  # mysql or postgresql
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '3306')
    DB_NAME = os.getenv('DB_NAME', 'westval')
    DB_USER = os.getenv('DB_USER', 'westval_user')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'westval_pass')
    
    @property
    def SQLALCHEMY_DATABASE_URI(self):
        if self.DB_TYPE == 'mysql':
            return f'mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4'
        else:
            return f'postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'max_overflow': 20
    }
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES_HOURS', '8')))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES_DAYS', '30')))
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    # File Upload
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', '/app/uploads')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 100 * 1024 * 1024))  # 100MB
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'png', 'jpg', 'jpeg', 'txt', 'csv'}
    
    # Redis
    REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
    REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
    REDIS_DB = int(os.getenv('REDIS_DB', '0'))
    REDIS_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'
    
    # Celery
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL
    
    # Active Directory / LDAP Configuration
    AUTH_TYPE = os.getenv('AUTH_TYPE', 'local')  # local, ldap, or ad
    
    # LDAP Settings
    LDAP_ENABLED = os.getenv('LDAP_ENABLED', 'false').lower() == 'true'
    LDAP_HOST = os.getenv('LDAP_HOST', 'ldap://your-ad-server.com')
    LDAP_PORT = int(os.getenv('LDAP_PORT', '389'))
    LDAP_USE_SSL = os.getenv('LDAP_USE_SSL', 'false').lower() == 'true'
    LDAP_BASE_DN = os.getenv('LDAP_BASE_DN', 'dc=example,dc=com')
    LDAP_USER_DN = os.getenv('LDAP_USER_DN', 'ou=users,dc=example,dc=com')
    LDAP_BIND_USER = os.getenv('LDAP_BIND_USER', '')
    LDAP_BIND_PASSWORD = os.getenv('LDAP_BIND_PASSWORD', '')
    LDAP_USERNAME_ATTRIBUTE = os.getenv('LDAP_USERNAME_ATTRIBUTE', 'sAMAccountName')
    LDAP_EMAIL_ATTRIBUTE = os.getenv('LDAP_EMAIL_ATTRIBUTE', 'mail')
    LDAP_FIRSTNAME_ATTRIBUTE = os.getenv('LDAP_FIRSTNAME_ATTRIBUTE', 'givenName')
    LDAP_LASTNAME_ATTRIBUTE = os.getenv('LDAP_LASTNAME_ATTRIBUTE', 'sn')
    LDAP_GROUP_SEARCH_BASE = os.getenv('LDAP_GROUP_SEARCH_BASE', 'ou=groups,dc=example,dc=com')
    
    # Active Directory Specific
    AD_DOMAIN = os.getenv('AD_DOMAIN', 'EXAMPLE')
    AD_SERVER = os.getenv('AD_SERVER', 'ad.example.com')
    AD_SEARCH_BASE = os.getenv('AD_SEARCH_BASE', 'DC=example,DC=com')
    
    # Email Configuration (for notifications)
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@westval.com')
    
    # OpenAI API
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4')
    
    # Application Settings
    COMPANY_NAME = os.getenv('COMPANY_NAME', 'Westval')
    SYSTEM_EMAIL = os.getenv('SYSTEM_EMAIL', 'system@westval.com')
    PAGINATION_PER_PAGE = int(os.getenv('PAGINATION_PER_PAGE', '50'))
    
    # 21 CFR Part 11 Settings
    PASSWORD_MIN_LENGTH = int(os.getenv('PASSWORD_MIN_LENGTH', '8'))
    PASSWORD_REQUIRE_UPPERCASE = os.getenv('PASSWORD_REQUIRE_UPPERCASE', 'true').lower() == 'true'
    PASSWORD_REQUIRE_LOWERCASE = os.getenv('PASSWORD_REQUIRE_LOWERCASE', 'true').lower() == 'true'
    PASSWORD_REQUIRE_NUMBERS = os.getenv('PASSWORD_REQUIRE_NUMBERS', 'true').lower() == 'true'
    PASSWORD_REQUIRE_SPECIAL = os.getenv('PASSWORD_REQUIRE_SPECIAL', 'true').lower() == 'true'
    PASSWORD_EXPIRY_DAYS = int(os.getenv('PASSWORD_EXPIRY_DAYS', '90'))
    SESSION_TIMEOUT_MINUTES = int(os.getenv('SESSION_TIMEOUT_MINUTES', '30'))
    MAX_LOGIN_ATTEMPTS = int(os.getenv('MAX_LOGIN_ATTEMPTS', '3'))
    ACCOUNT_LOCKOUT_DURATION_MINUTES = int(os.getenv('ACCOUNT_LOCKOUT_DURATION_MINUTES', '30'))

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}