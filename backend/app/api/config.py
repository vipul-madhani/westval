"""System configuration API"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
import os

config_bp = Blueprint('config', __name__)

@config_bp.route('/settings', methods=['GET'])
@jwt_required()
def get_system_settings():
    """Get system configuration (admin only)"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or not user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    from flask import current_app
    
    # Return non-sensitive configuration
    settings = {
        'general': {
            'company_name': current_app.config['COMPANY_NAME'],
            'system_email': current_app.config['SYSTEM_EMAIL'],
            'pagination_per_page': current_app.config['PAGINATION_PER_PAGE']
        },
        'authentication': {
            'auth_type': current_app.config['AUTH_TYPE'],
            'ldap_enabled': current_app.config['LDAP_ENABLED'],
            'ldap_host': current_app.config['LDAP_HOST'] if current_app.config['LDAP_ENABLED'] else None,
            'ad_domain': current_app.config['AD_DOMAIN'] if current_app.config['AUTH_TYPE'] == 'ad' else None,
            'ad_server': current_app.config['AD_SERVER'] if current_app.config['AUTH_TYPE'] == 'ad' else None
        },
        'security': {
            'password_min_length': current_app.config['PASSWORD_MIN_LENGTH'],
            'password_require_uppercase': current_app.config['PASSWORD_REQUIRE_UPPERCASE'],
            'password_require_lowercase': current_app.config['PASSWORD_REQUIRE_LOWERCASE'],
            'password_require_numbers': current_app.config['PASSWORD_REQUIRE_NUMBERS'],
            'password_require_special': current_app.config['PASSWORD_REQUIRE_SPECIAL'],
            'password_expiry_days': current_app.config['PASSWORD_EXPIRY_DAYS'],
            'session_timeout_minutes': current_app.config['SESSION_TIMEOUT_MINUTES'],
            'max_login_attempts': current_app.config['MAX_LOGIN_ATTEMPTS'],
            'account_lockout_duration_minutes': current_app.config['ACCOUNT_LOCKOUT_DURATION_MINUTES']
        },
        'database': {
            'type': current_app.config['DB_TYPE'],
            'host': current_app.config['DB_HOST'],
            'port': current_app.config['DB_PORT'],
            'name': current_app.config['DB_NAME']
        },
        'email': {
            'mail_server': current_app.config['MAIL_SERVER'],
            'mail_port': current_app.config['MAIL_PORT'],
            'mail_use_tls': current_app.config['MAIL_USE_TLS'],
            'mail_default_sender': current_app.config['MAIL_DEFAULT_SENDER']
        },
        'file_upload': {
            'max_content_length': current_app.config['MAX_CONTENT_LENGTH'],
            'allowed_extensions': list(current_app.config['ALLOWED_EXTENSIONS'])
        }
    }
    
    return jsonify(settings), 200

@config_bp.route('/settings/test-ldap', methods=['POST'])
@jwt_required()
def test_ldap_connection():
    """Test LDAP/AD connection (admin only)"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or not user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    from app.services.ldap_service import LDAPService
    from flask import current_app
    
    if not current_app.config['LDAP_ENABLED']:
        return jsonify({'error': 'LDAP is not enabled'}), 400
    
    data = request.get_json()
    test_username = data.get('username')
    test_password = data.get('password')
    
    if not test_username or not test_password:
        return jsonify({'error': 'Username and password required for testing'}), 400
    
    try:
        result = LDAPService.authenticate(test_username, test_password)
        
        if result:
            return jsonify({
                'success': True,
                'message': 'LDAP connection successful',
                'user_data': {
                    'username': result['username'],
                    'email': result['email'],
                    'first_name': result['first_name'],
                    'last_name': result['last_name'],
                    'groups': result.get('groups', [])[:5]  # Show first 5 groups
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'LDAP authentication failed - invalid credentials or connection error'
            }), 401
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'LDAP connection error: {str(e)}'
        }), 500

@config_bp.route('/settings/database-info', methods=['GET'])
@jwt_required()
def get_database_info():
    """Get database connection info (admin only)"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or not user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    from app import db
    from flask import current_app
    
    try:
        # Test database connection
        db.session.execute(db.text('SELECT 1'))
        
        # Get table count
        if current_app.config['DB_TYPE'] == 'mysql':
            result = db.session.execute(db.text(
                f"SELECT COUNT(*) as count FROM information_schema.tables WHERE table_schema = '{current_app.config['DB_NAME']}'"
            ))
        else:
            result = db.session.execute(db.text(
                "SELECT COUNT(*) as count FROM information_schema.tables WHERE table_schema = 'public'"
            ))
        
        table_count = result.scalar()
        
        return jsonify({
            'connected': True,
            'db_type': current_app.config['DB_TYPE'],
            'db_name': current_app.config['DB_NAME'],
            'db_host': current_app.config['DB_HOST'],
            'table_count': table_count
        }), 200
    
    except Exception as e:
        return jsonify({
            'connected': False,
            'error': str(e)
        }), 500