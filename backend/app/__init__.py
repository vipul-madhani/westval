"""Westval Application Factory"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from flask_caching import Cache
from config import Config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
socketio = SocketIO(cors_allowed_origins="*")
cache = Cache()

def create_app(config_class=Config):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    socketio.init_app(app)
    cache.init_app(app)
    CORS(app)
    
    # Register blueprints
    from app.api.auth import auth_bp
    from app.api.validation import validation_bp
    from app.api.documents import documents_bp
    from app.api.requirements import requirements_bp
    from app.api.tests import tests_bp
    from app.api.risk import risk_bp
    from app.api.compliance import compliance_bp
    from app.api.integrations import integrations_bp
    from app.api.ai import ai_bp
    from app.api.users import users_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(validation_bp, url_prefix='/api/validation')
    app.register_blueprint(documents_bp, url_prefix='/api/documents')
    app.register_blueprint(requirements_bp, url_prefix='/api/requirements')
    app.register_blueprint(tests_bp, url_prefix='/api/tests')
    app.register_blueprint(risk_bp, url_prefix='/api/risk')
    app.register_blueprint(compliance_bp, url_prefix='/api/compliance')
    app.register_blueprint(integrations_bp, url_prefix='/api/integrations')
    app.register_blueprint(ai_bp, url_prefix='/api/ai')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'version': '1.0.0'}, 200
    
    return app