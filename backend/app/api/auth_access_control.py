from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from functools import wraps
from app.services.auth_access_control_service import AccessControlService
from app.models.auth_access_control import AccessLog
from app import db
from datetime import datetime

auth_access_control_bp = Blueprint('auth_access_control', __name__, url_prefix='/api/auth')

def get_client_ip():
    return request.remote_addr or request.environ.get('HTTP_X_REAL_IP')

def require_mfa(f):
    @wraps(f)
    @jwt_required()
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        session = AccessControlService.validate_session(token)
        if not session or not session.mfa_verified:
            return jsonify({"error": "MFA verification required"}), 403
        return f(*args, **kwargs)
    return decorated

@auth_access_control_bp.route('/login-with-mfa', methods=['POST'])
def login_with_mfa():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    mfa_token = data.get('mfa_token')
    
    if not all([username, password, mfa_token]):
        return jsonify({"error": "Missing credentials"}), 400
    
    ip_address = get_client_ip()
    user_agent = request.headers.get('User-Agent', 'Unknown')
    
    try:
        from app.models.user import User
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.verify_password(password):
            AccessControlService.record_failed_login(user.id if user else username, ip_address)
            AccessControlService.log_access(
                user.id if user else username, 'LOGIN_FAILED', 'AUTH', ip_address, 'FAILED',
                details={"reason": "Invalid credentials"}
            )
            return jsonify({"error": "Invalid credentials"}), 401
        
        is_locked, lockout_minutes = AccessControlService.check_account_lockout(user.id, ip_address)
        if is_locked:
            AccessControlService.log_access(
                user.id, 'LOGIN_BLOCKED', 'AUTH', ip_address, 'BLOCKED',
                details={"reason": f"Account locked for {lockout_minutes:.1f} more minutes"}
            )
            return jsonify({"error": f"Account locked. Try again in {lockout_minutes:.0f} minutes"}), 403
        
        if not AccessControlService.verify_mfa(user.id, mfa_token):
            AccessControlService.record_failed_login(user.id, ip_address)
            return jsonify({"error": "Invalid MFA token"}), 401
        
        session = AccessControlService.create_session(user.id, ip_address, user_agent, mfa_verified=True)
        AccessControlService.reset_failed_login(user.id, ip_address)
        AccessControlService.log_access(
            user.id, 'LOGIN_SUCCESS', 'AUTH', ip_address, 'SUCCESS', session_id=session.id
        )
        
        return jsonify({
            "token": session.token,
            "expires_at": session.expires_at.isoformat(),
            "user_id": user.id
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_access_control_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    try:
        user_id = get_jwt_identity()
        from app.models.auth_access_control import UserSession, SessionStatus
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        session = UserSession.query.filter_by(token=token).first()
        if session:
            session.status = SessionStatus.REVOKED
            db.session.commit()
        
        AccessControlService.log_access(
            user_id, 'LOGOUT', 'AUTH', get_client_ip(), 'SUCCESS', session_id=session.id if session else None
        )
        return jsonify({"message": "Logged out successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_access_control_bp.route('/password/change', methods=['POST'])
@jwt_required()
def change_password():
    user_id = get_jwt_identity()
    data = request.get_json()
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    if not all([old_password, new_password]):
        return jsonify({"error": "Missing passwords"}), 400
    
    try:
        from app.models.user import User
        user = User.query.get(user_id)
        if not user.verify_password(old_password):
            AccessControlService.log_access(
                user_id, 'PASSWORD_CHANGE_FAILED', 'AUTH', get_client_ip(), 'FAILED',
                details={"reason": "Invalid old password"}
            )
            return jsonify({"error": "Invalid old password"}), 401
        
        success, message = AccessControlService.set_password(user_id, new_password)
        if not success:
            return jsonify({"error": message[0] if message else "Password change failed"}), 400
        
        AccessControlService.log_access(
            user_id, 'PASSWORD_CHANGED', 'AUTH', get_client_ip(), 'SUCCESS'
        )
        return jsonify({"message": "Password changed successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_access_control_bp.route('/access-log', methods=['GET'])
@require_mfa
def get_access_log():
    try:
        user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 50, type=int)
        
        logs = AccessLog.query.filter_by(user_id=user_id).order_by(
            AccessLog.timestamp.desc()
        ).paginate(page=page, per_page=limit)
        
        return jsonify({
            "logs": [
                {
                    "id": log.id,
                    "action": log.action,
                    "resource_type": log.resource_type,
                    "status": log.status,
                    "ip_address": log.ip_address,
                    "timestamp": log.timestamp.isoformat()
                }
                for log in logs.items
            ],
            "pagination": {
                "page": page,
                "total_pages": logs.pages,
                "total_items": logs.total
            }
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_access_control_bp.route('/mfa/setup', methods=['POST'])
@jwt_required()
def setup_mfa():
    user_id = get_jwt_identity()
    try:
        uri, secret = AccessControlService.setup_mfa(user_id)
        if not uri:
            return jsonify({"error": "Failed to setup MFA"}), 500
        
        AccessControlService.log_access(
            user_id, 'MFA_SETUP', 'AUTH', get_client_ip(), 'SUCCESS'
        )
        return jsonify({"provisioning_uri": uri, "secret": secret}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
