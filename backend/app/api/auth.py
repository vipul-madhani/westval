"""Authentication endpoints with LDAP/AD support"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app import db
from app.models.user import User, Role
from app.services.ldap_service import LDAPService
from datetime import datetime
import uuid

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login with local or LDAP/AD authentication"""
    data = request.get_json()
    username = data.get('username') or data.get('email')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    from flask import current_app
    
    # Check if LDAP is enabled
    if current_app.config['LDAP_ENABLED']:
        # Try LDAP authentication
        ldap_user_data = LDAPService.authenticate(username, password)
        
        if ldap_user_data:
            # LDAP auth successful - sync user to local database
            user = User.query.filter(
                (User.username == ldap_user_data['username']) |
                (User.email == ldap_user_data['email'])
            ).first()
            
            if not user:
                # Create new user from LDAP
                user = User(
                    id=str(uuid.uuid4()),
                    username=ldap_user_data['username'],
                    email=ldap_user_data['email'],
                    first_name=ldap_user_data['first_name'],
                    last_name=ldap_user_data['last_name'],
                    is_active=True,
                    is_ldap_user=True,
                    department=ldap_user_data.get('department', ''),
                    job_title=ldap_user_data.get('job_title', '')
                )
                
                # Map AD groups to roles
                role_names = LDAPService.map_ad_groups_to_roles(ldap_user_data.get('groups', []))
                for role_name in role_names:
                    role = Role.query.filter_by(name=role_name).first()
                    if role:
                        user.roles.append(role)
                
                db.session.add(user)
                db.session.commit()
            else:
                # Update existing user
                user.first_name = ldap_user_data['first_name']
                user.last_name = ldap_user_data['last_name']
                user.email = ldap_user_data['email']
                user.last_login = datetime.utcnow()
                
                # Update roles from AD groups
                role_names = LDAPService.map_ad_groups_to_roles(ldap_user_data.get('groups', []))
                user.roles = []
                for role_name in role_names:
                    role = Role.query.filter_by(name=role_name).first()
                    if role:
                        user.roles.append(role)
                
                db.session.commit()
            
            # Generate tokens
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)
            
            return jsonify({
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'roles': [r.role.name for r in user.roles],
                    'auth_method': 'ldap'
                }
            }), 200
    
    # Local authentication (fallback)
    user = User.query.filter(
        (User.username == username) | (User.email == username)
    ).first()
    
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'Account is inactive'}), 401
    
    # Check if account is locked
    if user.is_locked:
        return jsonify({'error': 'Account is locked due to multiple failed login attempts'}), 401
    
    # Verify password (only for local users)
    if not user.is_ldap_user and not user.check_password(password):
        # Increment failed attempts
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= current_app.config['MAX_LOGIN_ATTEMPTS']:
            user.is_locked = True
            user.locked_until = datetime.utcnow() + timedelta(minutes=current_app.config['ACCOUNT_LOCKOUT_DURATION_MINUTES'])
        db.session.commit()
        
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Reset failed attempts on successful login
    user.failed_login_attempts = 0
    user.is_locked = False
    user.locked_until = None
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # Generate tokens
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'roles': [r.role.name for r in user.roles],
            'auth_method': 'local'
        }
    }), 200

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    user_id = get_jwt_identity()
    access_token = create_access_token(identity=user_id)
    return jsonify({'access_token': access_token}), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user info"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'department': user.department,
        'job_title': user.job_title,
        'roles': [r.name for r in user.roles],
        'is_admin': user.is_admin,
        'is_ldap_user': user.is_ldap_user
    }), 200