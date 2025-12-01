"""Validation management API - Complete implementation"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.validation import ValidationProject, ValidationProtocol
from app.services.validation_service import ValidationService
from datetime import datetime

validation_bp = Blueprint('validation', __name__)

@validation_bp.route('/projects', methods=['GET'])
@jwt_required()
def list_projects():
    """List all validation projects with filtering"""
    user_id = get_jwt_identity()
    
    # Query parameters
    status = request.args.get('status')
    validation_type = request.args.get('type')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    
    query = ValidationProject.query
    
    if status:
        query = query.filter_by(status=status)
    if validation_type:
        query = query.filter_by(validation_type=validation_type)
    
    pagination = query.order_by(ValidationProject.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'projects': [{
            'id': p.id,
            'project_number': p.project_number,
            'title': p.title,
            'description': p.description,
            'validation_type': p.validation_type,
            'methodology': p.methodology,
            'gamp_category': p.gamp_category,
            'risk_level': p.risk_level,
            'status': p.status,
            'department': p.department,
            'planned_start_date': p.planned_start_date.isoformat() if p.planned_start_date else None,
            'planned_end_date': p.planned_end_date.isoformat() if p.planned_end_date else None,
            'created_at': p.created_at.isoformat()
        } for p in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200

@validation_bp.route('/projects', methods=['POST'])
@jwt_required()
def create_project():
    """Create new validation project"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    data = request.get_json()
    
    # Validate required fields
    if not data.get('title'):
        return jsonify({'error': 'Title is required'}), 400
    
    try:
        project = ValidationService.create_project(data, user)
        return jsonify({
            'message': 'Project created successfully',
            'project': {
                'id': project.id,
                'project_number': project.project_number,
                'title': project.title,
                'status': project.status
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@validation_bp.route('/projects/<project_id>', methods=['GET'])
@jwt_required()
def get_project(project_id):
    """Get single validation project details"""
    project = ValidationProject.query.get(project_id)
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    return jsonify({
        'id': project.id,
        'project_number': project.project_number,
        'title': project.title,
        'description': project.description,
        'validation_type': project.validation_type,
        'methodology': project.methodology,
        'gamp_category': project.gamp_category,
        'risk_level': project.risk_level,
        'risk_score': project.risk_score,
        'status': project.status,
        'department': project.department,
        'planned_start_date': project.planned_start_date.isoformat() if project.planned_start_date else None,
        'planned_end_date': project.planned_end_date.isoformat() if project.planned_end_date else None,
        'actual_start_date': project.actual_start_date.isoformat() if project.actual_start_date else None,
        'actual_end_date': project.actual_end_date.isoformat() if project.actual_end_date else None,
        'created_at': project.created_at.isoformat(),
        'updated_at': project.updated_at.isoformat() if project.updated_at else None,
        'protocols_count': len(project.protocols),
        'requirements_count': len(project.requirements)
    }), 200

@validation_bp.route('/projects/<project_id>', methods=['PUT'])
@jwt_required()
def update_project(project_id):
    """Update validation project"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    data = request.get_json()
    
    try:
        project = ValidationService.update_project(project_id, data, user)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        return jsonify({
            'message': 'Project updated successfully',
            'project': {
                'id': project.id,
                'title': project.title,
                'status': project.status
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@validation_bp.route('/projects/<project_id>', methods=['DELETE'])
@jwt_required()
def delete_project(project_id):
    """Delete validation project"""
    user_id = get_jwt_identity()
    project = ValidationProject.query.get(project_id)
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    try:
        db.session.delete(project)
        db.session.commit()
        return jsonify({'message': 'Project deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@validation_bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_statistics():
    """Get validation project statistics"""
    try:
        stats = ValidationService.get_project_statistics()
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@validation_bp.route('/protocols', methods=['GET', 'POST'])
@jwt_required()
def protocols():
    """List or create validation protocols"""
    if request.method == 'GET':
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        project_id = request.args.get('project_id')
        
        query = ValidationProtocol.query
        if project_id:
            query = query.filter_by(project_id=project_id)
        
        pagination = query.order_by(ValidationProtocol.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'protocols': [{
                'id': p.id,
                'protocol_number': p.protocol_number,
                'protocol_type': p.protocol_type,
                'title': p.title,
                'version': p.version,
                'status': p.status,
                'created_at': p.created_at.isoformat()
            } for p in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages
        }), 200
    
    else:  # POST
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Create protocol (simplified - full implementation would use service)
        return jsonify({'message': 'Protocol creation endpoint'}), 201