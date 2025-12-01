from flask import Blueprint, request, jsonify
from functools import wraps
from app.services.test_management_service import TestManagementService
from app import db

test_management_bp = Blueprint('test_management', __name__, url_prefix='/api/test-management')

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Missing authorization token'}), 401
        return f(*args, **kwargs)
    return decorated_function

# Test Plan Endpoints
@test_management_bp.route('/plans', methods=['POST'])
@require_auth
def create_test_plan():
    """Create new test plan"""
    data = request.get_json()
    try:
        plan = TestManagementService.create_test_plan(
            name=data['name'],
            description=data.get('description', ''),
            validation_id=data['validation_id'],
            project_id=data['project_id'],
            created_by=data['created_by']
        )
        return jsonify({
            'id': plan.id,
            'name': plan.name,
            'status': plan.status,
            'created_at': plan.created_at.isoformat()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@test_management_bp.route('/plans/<plan_id>', methods=['GET'])
@require_auth
def get_test_plan(plan_id):
    """Get test plan details"""
    plan = TestManagementService.get_test_plan(plan_id)
    if not plan:
        return jsonify({'error': 'Plan not found'}), 404
    return jsonify({
        'id': plan.id,
        'name': plan.name,
        'description': plan.description,
        'status': plan.status,
        'test_sets': len(plan.test_sets),
        'created_at': plan.created_at.isoformat()
    }), 200

# Test Set Endpoints
@test_management_bp.route('/plans/<plan_id>/sets', methods=['POST'])
@require_auth
def create_test_set(plan_id):
    """Create test set within plan"""
    data = request.get_json()
    try:
        test_set = TestManagementService.create_test_set(
            test_plan_id=plan_id,
            name=data['name'],
            description=data.get('description', ''),
            scope=data.get('scope', 'FUNCTIONAL')
        )
        return jsonify({
            'id': test_set.id,
            'name': test_set.name,
            'scope': test_set.scope
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Test Case Endpoints
@test_management_bp.route('/sets/<set_id>/cases', methods=['POST'])
@require_auth
def create_test_case(set_id):
    """Create test case"""
    data = request.get_json()
    try:
        test_case = TestManagementService.create_test_case(
            test_set_id=set_id,
            name=data['name'],
            description=data.get('description', ''),
            requirement_id=data.get('requirement_id')
        )
        return jsonify({
            'id': test_case.id,
            'name': test_case.name,
            'status': test_case.status
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Test Step Endpoints
@test_management_bp.route('/cases/<case_id>/steps', methods=['POST'])
@require_auth
def add_test_step(case_id):
    """Add step to test case"""
    data = request.get_json()
    try:
        step = TestManagementService.add_test_step(
            test_case_id=case_id,
            step_number=data['step_number'],
            action=data['action'],
            expected_result=data['expected_result']
        )
        return jsonify({
            'id': step.id,
            'step_number': step.step_number,
            'action': step.action
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Test Execution Endpoints
@test_management_bp.route('/cases/<case_id>/execute', methods=['POST'])
@require_auth
def execute_test(case_id):
    """Execute test case"""
    data = request.get_json()
    try:
        execution = TestManagementService.execute_test(
            test_case_id=case_id,
            executed_by=data['executed_by']
        )
        return jsonify({
            'id': execution.id,
            'status': execution.overall_status,
            'execution_date': execution.execution_date.isoformat()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@test_management_bp.route('/executions/<execution_id>/steps/<step_id>/result', methods=['POST'])
@require_auth
def record_step_result(execution_id, step_id):
    """Record test step result"""
    data = request.get_json()
    try:
        result = TestManagementService.record_step_result(
            execution_id=execution_id,
            step_id=step_id,
            status=data['status'],
            actual_result=data['actual_result'],
            notes=data.get('notes'),
            screenshots=data.get('screenshots', [])
        )
        return jsonify({
            'id': result.id,
            'status': result.status,
            'duration_seconds': result.duration_seconds
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Coverage & Analytics Endpoints
@test_management_bp.route('/validations/<validation_id>/coverage', methods=['GET'])
@require_auth
def get_test_coverage(validation_id):
    """Get test coverage metrics"""
    try:
        coverage = TestManagementService.get_test_coverage(validation_id)
        return jsonify(coverage), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@test_management_bp.route('/validations/<validation_id>/untested-requirements', methods=['GET'])
@require_auth
def get_untested_requirements(validation_id):
    """Get requirements not covered by tests"""
    try:
        untested = TestManagementService.get_untested_requirements(validation_id)
        return jsonify({
            'total_untested': len(untested),
            'requirements': [{'id': r.id, 'name': r.name} for r in untested]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Requirement Linking
@test_management_bp.route('/cases/<case_id>/link-requirement', methods=['POST'])
@require_auth
def link_requirement(case_id):
    """Link requirement to test case"""
    data = request.get_json()
    try:
        test_case = TestManagementService.link_requirement_to_test(
            test_case_id=case_id,
            requirement_id=data['requirement_id']
        )
        return jsonify({
            'id': test_case.id,
            'requirement_id': test_case.requirement_id
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Health check
@test_management_bp.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'}), 200
