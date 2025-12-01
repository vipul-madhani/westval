"""User management API"""
from flask import Blueprint

users_bp = Blueprint('users', __name__)

@users_bp.route('/', methods=['GET'])
def list_users():
    return {'message': 'Users endpoint'}, 200

@users_bp.route('/<user_id>', methods=['GET', 'PUT', 'DELETE'])
def user_detail(user_id):
    return {'message': f'User {user_id} endpoint'}, 200