from flask import Blueprint, request, jsonify
from functools import wraps
from datetime import datetime, timedelta
from ..models.system_validation import ValidationPhase
from ..services.system_validation_service import SystemValidationService
from ..models.audit import AuditLog
from sqlalchemy import db
import jwt
import os

validation_bp = Blueprint('validation', __name__, url_prefix='/api/validation')
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Missing auth token'}), 401
        try:
            data = jwt.decode(token.split(' ')[1], SECRET_KEY, algorithms=['HS256'])
            current_user_id = data['user_id']
        except:
            return jsonify({'message': 'Invalid token'}), 401
        return f(current_user_id, *args, **kwargs)
    return decorated

@validation_bp.route('/protocol', methods=['POST'])
@token_required
def create_protocol(current_user_id):
    try:
        data = request.get_json()
        protocol_name = data.get('protocol_name')
        phase = data.get('phase')
        scope = data.get('scope')
        acceptance_criteria = data.get('acceptance_criteria')
        
        protocol = SystemValidationService.create_validation_protocol(
            protocol_name, ValidationPhase[phase], scope, acceptance_criteria, current_user_id
        )
        
        audit_log = AuditLog(
            action='CREATE_VALIDATION_PROTOCOL',
            entity_type='ValidationProtocol',
            entity_id=protocol.id,
            user_id=current_user_id,
            details=f'Created validation protocol: {protocol_name}'
        )
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify({'protocol_id': protocol.id, 'name': protocol.protocol_name}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@validation_bp.route('/test/<int:protocol_id>', methods=['POST'])
@token_required
def execute_test(current_user_id, protocol_id):
    try:
        data = request.get_json()
        test_case = data.get('test_case')
        expected_outcome = data.get('expected_outcome')
        actual_outcome = data.get('actual_outcome')
        
        result = SystemValidationService.execute_validation_test(
            protocol_id, test_case, expected_outcome, actual_outcome, current_user_id
        )
        
        audit_log = AuditLog(
            action='EXECUTE_VALIDATION_TEST',
            entity_type='ValidationResult',
            entity_id=result.id,
            user_id=current_user_id,
            details=f'Test result: {'PASSED' if result.passed else 'FAILED'}'
        )
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify({'result_id': result.id, 'passed': result.passed}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@validation_bp.route('/approve/<int:protocol_id>', methods=['POST'])
@token_required
def approve_protocol(current_user_id, protocol_id):
    try:
        protocol = SystemValidationService.approve_protocol(protocol_id, current_user_id)
        
        audit_log = AuditLog(
            action='APPROVE_VALIDATION_PROTOCOL',
            entity_type='ValidationProtocol',
            entity_id=protocol_id,
            user_id=current_user_id,
            details=f'Validation protocol approved'
        )
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify({'status': 'APPROVED', 'approved_at': protocol.approved_at.isoformat()}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@validation_bp.route('/summary/<int:protocol_id>', methods=['GET'])
@token_required
def get_summary(current_user_id, protocol_id):
    try:
        summary = SystemValidationService.get_validation_summary(protocol_id)
        if not summary:
            return jsonify({'error': 'Protocol not found'}), 404
        return jsonify(summary), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@validation_bp.route('/audit-report', methods=['GET'])
@token_required
def get_audit_report(current_user_id):
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        start = datetime.fromisoformat(start_date) if start_date else datetime.utcnow() - timedelta(days=30)
        end = datetime.fromisoformat(end_date) if end_date else datetime.utcnow()
        
        report = SystemValidationService.generate_audit_report(start, end)
        return jsonify(report), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@validation_bp.route('/health-metric', methods=['POST'])
@token_required
def record_metric(current_user_id):
    try:
        data = request.get_json()
        metric = SystemValidationService.record_system_health_metric(
            data.get('metric_name'),
            data.get('metric_value'),
            data.get('threshold_min'),
            data.get('threshold_max')
        )
        return jsonify({'metric_id': metric.id, 'status': metric.status}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
