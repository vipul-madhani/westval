"""Requirements management API - Complete implementation"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.requirement import Requirement
import uuid
from datetime import datetime

requirements_bp = Blueprint('requirements', __name__)

@requirements_bp.route('/', methods=['GET'])
@jwt_required()
def list_requirements():
    """List requirements with filtering"""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    project_id = request.args.get('project_id')
    req_type = request.args.get('type')
    
    query = Requirement.query
    
    if project_id:
        query = query.filter_by(project_id=project_id)
    if req_type:
        query = query.filter_by(requirement_type=req_type)
    
    pagination = query.order_by(Requirement.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'requirements': [{
            'id': r.id,
            'requirement_id': r.requirement_id,
            'requirement_type': r.requirement_type,
            'title': r.title,
            'description': r.description,
            'priority': r.priority,
            'criticality': r.criticality,
            'status': r.status,
            'created_at': r.created_at.isoformat()
        } for r in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages
    }), 200

@requirements_bp.route('/', methods=['POST'])
@jwt_required()
def create_requirement():
    """Create new requirement"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    data = request.get_json()
    
    if not data.get('title') or not data.get('project_id'):
        return jsonify({'error': 'Title and project_id are required'}), 400
    
    requirement = Requirement(
        id=str(uuid.uuid4()),
        project_id=data['project_id'],
        requirement_id=data.get('requirement_id', f"REQ-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"),
        requirement_type=data.get('requirement_type', 'URS'),
        title=data['title'],
        description=data.get('description', ''),
        category=data.get('category'),
        priority=data.get('priority', 'Medium'),
        criticality=data.get('criticality', 'Non-Critical'),
        status='Draft',
        source=data.get('source'),
        rationale=data.get('rationale'),
        test_approach=data.get('test_approach'),
        acceptance_criteria=data.get('acceptance_criteria'),
        created_by=user.id
    )
    
    try:
        db.session.add(requirement)
        db.session.commit()
        
        return jsonify({
            'message': 'Requirement created successfully',
            'requirement': {
                'id': requirement.id,
                'requirement_id': requirement.requirement_id,
                'title': requirement.title,
                'status': requirement.status
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@requirements_bp.route('/<requirement_id>', methods=['GET'])
@jwt_required()
def get_requirement(requirement_id):
    """Get requirement details"""
    requirement = Requirement.query.get(requirement_id)
    
    if not requirement:
        return jsonify({'error': 'Requirement not found'}), 404
    
    return jsonify({
        'id': requirement.id,
        'requirement_id': requirement.requirement_id,
        'requirement_type': requirement.requirement_type,
        'title': requirement.title,
        'description': requirement.description,
        'category': requirement.category,
        'priority': requirement.priority,
        'criticality': requirement.criticality,
        'status': requirement.status,
        'source': requirement.source,
        'rationale': requirement.rationale,
        'test_approach': requirement.test_approach,
        'acceptance_criteria': requirement.acceptance_criteria,
        'created_at': requirement.created_at.isoformat(),
        'test_cases_count': len(requirement.test_cases)
    }), 200

@requirements_bp.route('/<requirement_id>', methods=['PUT'])
@jwt_required()
def update_requirement(requirement_id):
    """Update requirement"""
    requirement = Requirement.query.get(requirement_id)
    
    if not requirement:
        return jsonify({'error': 'Requirement not found'}), 404
    
    data = request.get_json()
    
    # Update fields
    for field in ['title', 'description', 'priority', 'criticality', 'status', 'category']:
        if field in data:
            setattr(requirement, field, data[field])
    
    try:
        db.session.commit()
        return jsonify({'message': 'Requirement updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@requirements_bp.route('/traceability-matrix', methods=['GET'])
@jwt_required()
def get_traceability_matrix():
    """Get requirements traceability matrix"""
    project_id = request.args.get('project_id')
    
    if not project_id:
        return jsonify({'error': 'project_id is required'}), 400
    
    requirements = Requirement.query.filter_by(project_id=project_id).all()
    
    matrix = []
    for req in requirements:
        matrix.append({
            'requirement_id': req.requirement_id,
            'title': req.title,
            'type': req.requirement_type,
            'criticality': req.criticality,
            'test_cases': [{
                'test_case_id': tc.test_case_id,
                'title': tc.title,
                'status': tc.status
            } for tc in req.test_cases],
            'coverage': 'Complete' if len(req.test_cases) > 0 else 'Incomplete'
        })
    
    return jsonify({
        'project_id': project_id,
        'total_requirements': len(requirements),
        'traced_requirements': len([r for r in requirements if len(r.test_cases) > 0]),
        'matrix': matrix
    }), 200