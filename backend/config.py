"""Application configuration"""
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    
    # Application
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://localhost:5432/westval'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_SIZE = int(os.getenv('DATABASE_POOL_SIZE', 10))
    SQLALCHEMY_ECHO = DEBUG
    
    # Redis
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Cache
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = REDIS_URL
    CACHE_DEFAULT_TIMEOUT = 300
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    # File Upload
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', '/tmp/westval/uploads')
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'csv', 'txt', 'png', 'jpg', 'jpeg'}
    
    # AI/ML
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    AI_MODEL = os.getenv('AI_MODEL', 'gpt-4')
    AI_TEMPERATURE = float(os.getenv('AI_TEMPERATURE', 0.7))
    
    # Email
    MAIL_SERVER = os.getenv('SMTP_SERVER', 'localhost')
    MAIL_PORT = int(os.getenv('SMTP_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('SMTP_USER')
    MAIL_PASSWORD = os.getenv('SMTP_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@westval.com')
    
    # Integrations
    JIRA_URL = os.getenv('JIRA_URL')
    JIRA_EMAIL = os.getenv('JIRA_EMAIL')
    JIRA_API_TOKEN = os.getenv('JIRA_API_TOKEN')
    
    AZURE_DEVOPS_ORGANIZATION = os.getenv('AZURE_DEVOPS_ORGANIZATION')
    AZURE_DEVOPS_PAT = os.getenv('AZURE_DEVOPS_PAT')
    
    # AWS S3
    S3_BUCKET = os.getenv('S3_BUCKET')
    S3_REGION = os.getenv('S3_REGION', 'us-east-1')
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    
    # Compliance
    ENABLE_AUDIT_TRAIL = True
    PASSWORD_MIN_LENGTH = 12
    PASSWORD_REQUIRE_SPECIAL_CHAR = True
    PASSWORD_REQUIRE_NUMBER = True
    PASSWORD_REQUIRE_UPPERCASE = True
    SESSION_TIMEOUT_MINUTES = int(os.getenv('SESSION_TIMEOUT_MINUTES', 30))
    
    # Features
    FEATURE_AI_GENERATION = os.getenv('FEATURE_AI_GENERATION', 'True').lower() == 'true'
    FEATURE_JIRA_INTEGRATION = os.getenv('FEATURE_JIRA_INTEGRATION', 'True').lower() == 'true'
    FEATURE_ADVANCED_ANALYTICS = os.getenv('FEATURE_ADVANCED_ANALYTICS', 'True').lower() == 'true'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_ECHO = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}