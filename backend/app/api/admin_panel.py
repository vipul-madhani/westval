from flask import Blueprint, request, jsonify
from functools import wraps
from ..services.admin_panel_service import AdminPanelService
from sqlalchemy import db
import jwt, os

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')
SECRET_KEY = os.getenv('SECRET_KEY', 'secret')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token: return jsonify({'error': 'Missing token'}), 401
        try:
            data = jwt.decode(token.split(' ')[1], SECRET_KEY, algorithms=['HS256'])
            current_user_id = data['user_id']
        except: return jsonify({'error': 'Invalid token'}), 401
        return f(current_user_id, *args, **kwargs)
    return decorated

@admin_bp.route('/role', methods=['POST'])
@token_required
def create_role(current_user_id):
    try:
        data = request.get_json()
        role = AdminPanelService.create_role(data['name'], data.get('description'), data.get('permissions', []))
        return jsonify({'role_id': role.id}), 201
    except Exception as e: return jsonify({'error': str(e)}), 500

@admin_bp.route('/permission', methods=['POST'])
@token_required
def assign_permission(current_user_id):
    try:
        data = request.get_json()
        perm = AdminPanelService.assign_permission(data['admin_user_id'], data['type'], data['resource'], current_user_id)
        return jsonify({'permission_id': perm.id}), 201
    except Exception as e: return jsonify({'error': str(e)}), 500

@admin_bp.route('/config', methods=['POST'])
@token_required
def set_config(current_user_id):
    try:
        data = request.get_json()
        config = AdminPanelService.set_system_config(data['key'], data['value'], data.get('type'), data.get('encrypted', False), current_user_id)
        return jsonify({'config_id': config.id}), 201
    except Exception as e: return jsonify({'error': str(e)}), 500

@admin_bp.route('/config/<key>', methods=['GET'])
@token_required
def get_config(current_user_id, key):
    try:
        config = AdminPanelService.get_system_config(key)
        if not config: return jsonify({'error': 'Not found'}), 404
        return jsonify({'key': config.config_key, 'value': config.config_value}), 200
    except Exception as e: return jsonify({'error': str(e)}), 500
