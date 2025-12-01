"""Validation management API"""
from flask import Blueprint

validation_bp = Blueprint('validation', __name__)

@validation_bp.route('/projects', methods=['GET', 'POST'])
def projects():
    """List or create validation projects"""
    return {'message': 'Validation projects endpoint'}, 200

@validation_bp.route('/projects/<project_id>', methods=['GET', 'PUT', 'DELETE'])
def project_detail(project_id):
    """Get, update, or delete validation project"""
    return {'message': f'Project {project_id} endpoint'}, 200

@validation_bp.route('/protocols', methods=['GET', 'POST'])
def protocols():
    """List or create validation protocols"""
    return {'message': 'Validation protocols endpoint'}, 200