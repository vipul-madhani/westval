"""Validation Projects API endpoints"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.validation import ValidationProject, ValidationProtocol
from app.models.user import User
from datetime import datetime, date
import uuid

validation_bp = Blueprint('validation', __name__)

@validation_bp.route('/projects', methods=['GET'])
@jwt_required()
def get_projects():
    """Get all validation projects with filters"""
    try:
        # Get query parameters
        status = request.args.get('status')
        validation_type = request.args.get('type')
        search = request.args.get('search')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        # Build query
        query = ValidationProject.query
        
        if status:
            query = query.filter(ValidationProject.status == status)
        if validation_type:
            query = query.filter(ValidationProject.validation_type == validation_type)
        if search:
            query = query.filter(
                db.or_(
                    ValidationProject.title.ilike(f'%{search}%'),
                    ValidationProject.project_number.ilike(f'%{search}%'),
                    ValidationProject.description.ilike(f'%{search}%')
                )
            )
        
        # Paginate
        pagination = query.order_by(ValidationProject.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        projects = []
        for project in pagination.items:
            owner = User.query.get(project.owner_id) if project.owner_id else None
            projects.append({
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
                'owner': {
                    'id': owner.id,
                    'name': f'{owner.first_name} {owner.last_name}',
                    'email': owner.email
                } if owner else None,
                'department': project.department,
                'planned_start_date': project.planned_start_date.isoformat() if project.planned_start_date else None,
                'planned_end_date': project.planned_end_date.isoformat() if project.planned_end_date else None,
                'actual_start_date': project.actual_start_date.isoformat() if project.actual_start_date else None,
                'actual_end_date': project.actual_end_date.isoformat() if project.actual_end_date else None,
                'created_at': project.created_at.isoformat() if project.created_at else None,
                'updated_at': project.updated_at.isoformat() if project.updated_at else None
            })
        
        return jsonify({
            'projects': projects,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@validation_bp.route('/projects/<project_id>', methods=['GET'])
@jwt_required()
def get_project(project_id):
    """Get a single validation project"""
    try:
        project = ValidationProject.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        owner = User.query.get(project.owner_id) if project.owner_id else None
        created_by_user = User.query.get(project.created_by) if project.created_by else None
        
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
            'owner': {
                'id': owner.id,
                'name': f'{owner.first_name} {owner.last_name}',
                'email': owner.email
            } if owner else None,
            'department': project.department,
            'planned_start_date': project.planned_start_date.isoformat() if project.planned_start_date else None,
            'planned_end_date': project.planned_end_date.isoformat() if project.planned_end_date else None,
            'actual_start_date': project.actual_start_date.isoformat() if project.actual_start_date else None,
            'actual_end_date': project.actual_end_date.isoformat() if project.actual_end_date else None,
            'created_at': project.created_at.isoformat() if project.created_at else None,
            'updated_at': project.updated_at.isoformat() if project.updated_at else None,
            'created_by': {
                'id': created_by_user.id,
                'name': f'{created_by_user.first_name} {created_by_user.last_name}'
            } if created_by_user else None,
            'protocols_count': len(project.protocols),
            'requirements_count': len(project.requirements),
            'risks_count': len(project.risks)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@validation_bp.route('/projects', methods=['POST'])
@jwt_required()
def create_project():
    """Create a new validation project"""
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        
        # Generate project number if not provided
        project_number = data.get('project_number')
        if not project_number:
            # Auto-generate: VAL-YYYY-NNNN
            year = datetime.now().year
            count = ValidationProject.query.filter(
                ValidationProject.project_number.like(f'VAL-{year}-%')
            ).count()
            project_number = f'VAL-{year}-{count + 1:04d}'
        
        project = ValidationProject(
            id=str(uuid.uuid4()),
            project_number=project_number,
            title=data.get('title'),
            description=data.get('description'),
            validation_type=data.get('validation_type'),
            methodology=data.get('methodology'),
            gamp_category=data.get('gamp_category'),
            risk_level=data.get('risk_level'),
            risk_score=data.get('risk_score'),
            status=data.get('status', 'Planning'),
            owner_id=data.get('owner_id', user_id),
            department=data.get('department'),
            planned_start_date=datetime.fromisoformat(data['planned_start_date']).date() if data.get('planned_start_date') else None,
            planned_end_date=datetime.fromisoformat(data['planned_end_date']).date() if data.get('planned_end_date') else None,
            created_by=user_id
        )
        
        db.session.add(project)
        db.session.commit()
        
        return jsonify({
            'message': 'Project created successfully',
            'project_id': project.id,
            'project_number': project.project_number
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@validation_bp.route('/projects/<project_id>', methods=['PUT'])
@jwt_required()
def update_project(project_id):
    """Update a validation project"""
    try:
        project = ValidationProject.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        data = request.get_json()
        
        # Update fields
        if 'title' in data:
            project.title = data['title']
        if 'description' in data:
            project.description = data['description']
        if 'validation_type' in data:
            project.validation_type = data['validation_type']
        if 'methodology' in data:
            project.methodology = data['methodology']
        if 'gamp_category' in data:
            project.gamp_category = data['gamp_category']
        if 'risk_level' in data:
            project.risk_level = data['risk_level']
        if 'risk_score' in data:
            project.risk_score = data['risk_score']
        if 'status' in data:
            project.status = data['status']
        if 'owner_id' in data:
            project.owner_id = data['owner_id']
        if 'department' in data:
            project.department = data['department']
        if 'planned_start_date' in data:
            project.planned_start_date = datetime.fromisoformat(data['planned_start_date']).date() if data['planned_start_date'] else None
        if 'planned_end_date' in data:
            project.planned_end_date = datetime.fromisoformat(data['planned_end_date']).date() if data['planned_end_date'] else None
        if 'actual_start_date' in data:
            project.actual_start_date = datetime.fromisoformat(data['actual_start_date']).date() if data['actual_start_date'] else None
        if 'actual_end_date' in data:
            project.actual_end_date = datetime.fromisoformat(data['actual_end_date']).date() if data['actual_end_date'] else None
        
        project.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Project updated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@validation_bp.route('/projects/<project_id>', methods=['DELETE'])
@jwt_required()
def delete_project(project_id):
    """Delete a validation project"""
    try:
        project = ValidationProject.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        db.session.delete(project)
        db.session.commit()
        
        return jsonify({'message': 'Project deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@validation_bp.route('/projects/<project_id>/statistics', methods=['GET'])
@jwt_required()
def get_project_statistics(project_id):
    """Get project statistics"""
    try:
        project = ValidationProject.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Calculate statistics
        total_requirements = len(project.requirements)
        total_risks = len(project.risks)
        total_protocols = len(project.protocols)
        
        # Calculate progress (simplified - based on status)
        status_progress = {
            'Planning': 10,
            'In Progress': 50,
            'Testing': 70,
            'Review': 85,
            'Approved': 95,
            'Closed': 100
        }
        progress = status_progress.get(project.status, 0)
        
        return jsonify({
            'project_id': project.id,
            'progress': progress,
            'total_requirements': total_requirements,
            'total_risks': total_risks,
            'total_protocols': total_protocols,
            'status': project.status,
            'risk_level': project.risk_level
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500