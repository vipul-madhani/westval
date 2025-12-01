"""Test management API - Complete implementation"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.test import TestCase, Deviation
import uuid
from datetime import datetime

tests_bp = Blueprint('tests', __name__)

@tests_bp.route('/', methods=['GET'])
@jwt_required()
def list_test_cases():
    """List test cases"""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    protocol_id = request.args.get('protocol_id')
    status = request.args.get('status')
    
    query = TestCase.query
    
    if protocol_id:
        query = query.filter_by(protocol_id=protocol_id)
    if status:
        query = query.filter_by(status=status)
    
    pagination = query.order_by(TestCase.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'test_cases': [{
            'id': tc.id,
            'test_case_id': tc.test_case_id,
            'title': tc.title,
            'test_type': tc.test_type,
            'priority': tc.priority,
            'status': tc.status,
            'is_gxp_critical': tc.is_gxp_critical,
            'executed_at': tc.executed_at.isoformat() if tc.executed_at else None
        } for tc in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages
    }), 200

@tests_bp.route('/', methods=['POST'])
@jwt_required()
def create_test_case():
    """Create new test case"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data.get('title') or not data.get('protocol_id'):
        return jsonify({'error': 'Title and protocol_id are required'}), 400
    
    test_case = TestCase(
        id=str(uuid.uuid4()),
        protocol_id=data['protocol_id'],
        test_case_id=data.get('test_case_id', f"TC-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"),
        title=data['title'],
        objective=data.get('objective'),
        test_type=data.get('test_type', 'IQ'),
        test_category=data.get('test_category'),
        priority=data.get('priority', 'Medium'),
        is_gxp_critical=data.get('is_gxp_critical', True),
        prerequisites=data.get('prerequisites'),
        test_steps=data.get('test_steps', []),
        expected_result=data.get('expected_result'),
        acceptance_criteria=data.get('acceptance_criteria'),
        status='Not Executed'
    )
    
    try:
        db.session.add(test_case)
        db.session.commit()
        
        return jsonify({
            'message': 'Test case created successfully',
            'test_case': {
                'id': test_case.id,
                'test_case_id': test_case.test_case_id,
                'title': test_case.title
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@tests_bp.route('/<test_case_id>/execute', methods=['POST'])
@jwt_required()
def execute_test_case(test_case_id):
    """Execute test case and record results"""
    user_id = get_jwt_identity()
    test_case = TestCase.query.get(test_case_id)
    
    if not test_case:
        return jsonify({'error': 'Test case not found'}), 404
    
    data = request.get_json()
    
    test_case.status = data.get('status', 'Passed')
    test_case.actual_result = data.get('actual_result')
    test_case.executed_at = datetime.utcnow()
    test_case.executed_by = user_id
    test_case.evidence_files = data.get('evidence_files', [])
    
    # If failed, create deviation
    if test_case.status == 'Failed':
        test_case.has_deviation = True
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Test case executed successfully',
            'test_case': {
                'id': test_case.id,
                'status': test_case.status,
                'executed_at': test_case.executed_at.isoformat()
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@tests_bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_test_statistics():
    """Get test execution statistics"""
    protocol_id = request.args.get('protocol_id')
    
    query = TestCase.query
    if protocol_id:
        query = query.filter_by(protocol_id=protocol_id)
    
    total = query.count()
    passed = query.filter_by(status='Passed').count()
    failed = query.filter_by(status='Failed').count()
    not_executed = query.filter_by(status='Not Executed').count()
    
    return jsonify({
        'total': total,
        'passed': passed,
        'failed': failed,
        'not_executed': not_executed,
        'pass_rate': round((passed / total * 100) if total > 0 else 0, 2)
    }), 200