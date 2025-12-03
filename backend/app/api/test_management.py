"""Test Management API endpoints"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.test_management import TestPlan, TestSet, TestCase, TestStep, TestExecution, TestStepResult
from app.models.user import User
from datetime import datetime
import uuid

tests_bp = Blueprint('tests', __name__)

# ==================== TEST PLANS ====================

@tests_bp.route('/plans', methods=['GET'])
@jwt_required()
def get_test_plans():
    """Get all test plans with optional filtering"""
    try:
        project_id = request.args.get('project_id')
        status = request.args.get('status')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        query = TestPlan.query
        
        if project_id:
            query = query.filter(TestPlan.project_id == project_id)
        if status:
            query = query.filter(TestPlan.status == status)
        
        pagination = query.order_by(TestPlan.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        plans = []
        for plan in pagination.items:
            creator = User.query.get(plan.created_by) if plan.created_by else None
            plans.append({
                'id': plan.id,
                'project_id': plan.project_id,
                'name': plan.name,
                'description': plan.description,
                'status': plan.status,
                'created_by': {
                    'id': creator.id,
                    'name': f'{creator.first_name} {creator.last_name}'
                } if creator else None,
                'created_at': plan.created_at.isoformat() if plan.created_at else None,
                'test_cases_count': len(plan.test_cases),
                'test_sets_count': len(plan.test_sets)
            })
        
        return jsonify({
            'plans': plans,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tests_bp.route('/plans', methods=['POST'])
@jwt_required()
def create_test_plan():
    """Create a new test plan"""
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        
        plan = TestPlan(
            id=str(uuid.uuid4()),
            project_id=data.get('project_id'),
            name=data.get('name'),
            description=data.get('description'),
            status=data.get('status', 'Draft'),
            created_by=user_id
        )
        
        db.session.add(plan)
        db.session.commit()
        
        return jsonify({
            'message': 'Test plan created successfully',
            'plan_id': plan.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@tests_bp.route('/plans/<plan_id>', methods=['GET'])
@jwt_required()
def get_test_plan(plan_id):
    """Get a single test plan with details"""
    try:
        plan = TestPlan.query.get(plan_id)
        if not plan:
            return jsonify({'error': 'Test plan not found'}), 404
        
        creator = User.query.get(plan.created_by) if plan.created_by else None
        
        return jsonify({
            'id': plan.id,
            'project_id': plan.project_id,
            'name': plan.name,
            'description': plan.description,
            'status': plan.status,
            'created_by': {
                'id': creator.id,
                'name': f'{creator.first_name} {creator.last_name}'
            } if creator else None,
            'created_at': plan.created_at.isoformat() if plan.created_at else None,
            'test_cases_count': len(plan.test_cases),
            'test_sets_count': len(plan.test_sets)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== TEST CASES ====================

@tests_bp.route('/cases', methods=['GET'])
@jwt_required()
def get_test_cases():
    """Get all test cases with optional filtering"""
    try:
        plan_id = request.args.get('plan_id')
        set_id = request.args.get('set_id')
        status = request.args.get('status')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        
        query = TestCase.query
        
        if plan_id:
            query = query.filter(TestCase.plan_id == plan_id)
        if set_id:
            query = query.filter(TestCase.set_id == set_id)
        if status:
            query = query.filter(TestCase.status == status)
        
        pagination = query.order_by(TestCase.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        cases = []
        for case in pagination.items:
            cases.append({
                'id': case.id,
                'plan_id': case.plan_id,
                'set_id': case.set_id,
                'requirement_id': case.requirement_id,
                'name': case.name,
                'description': case.description,
                'test_type': case.test_type,
                'priority': case.priority,
                'status': case.status,
                'steps_count': len(case.test_steps),
                'executions_count': len(case.test_executions),
                'created_at': case.created_at.isoformat() if case.created_at else None
            })
        
        return jsonify({
            'cases': cases,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tests_bp.route('/cases', methods=['POST'])
@jwt_required()
def create_test_case():
    """Create a new test case"""
    try:
        data = request.get_json()
        
        case = TestCase(
            id=str(uuid.uuid4()),
            plan_id=data.get('plan_id'),
            set_id=data.get('set_id'),
            requirement_id=data.get('requirement_id'),
            name=data.get('name'),
            description=data.get('description'),
            preconditions=data.get('preconditions'),
            test_type=data.get('test_type'),
            priority=data.get('priority', 3),
            status=data.get('status', 'Draft')
        )
        
        db.session.add(case)
        
        # Add test steps if provided
        if 'steps' in data:
            for step_data in data['steps']:
                step = TestStep(
                    id=str(uuid.uuid4()),
                    test_case_id=case.id,
                    step_number=step_data.get('step_number'),
                    action=step_data.get('action'),
                    expected_result=step_data.get('expected_result'),
                    test_data=step_data.get('test_data')
                )
                db.session.add(step)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Test case created successfully',
            'case_id': case.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@tests_bp.route('/cases/<case_id>', methods=['GET'])
@jwt_required()
def get_test_case(case_id):
    """Get a single test case with all steps"""
    try:
        case = TestCase.query.get(case_id)
        if not case:
            return jsonify({'error': 'Test case not found'}), 404
        
        steps = []
        for step in sorted(case.test_steps, key=lambda x: x.step_number):
            steps.append({
                'id': step.id,
                'step_number': step.step_number,
                'action': step.action,
                'expected_result': step.expected_result,
                'test_data': step.test_data
            })
        
        return jsonify({
            'id': case.id,
            'plan_id': case.plan_id,
            'set_id': case.set_id,
            'requirement_id': case.requirement_id,
            'name': case.name,
            'description': case.description,
            'preconditions': case.preconditions,
            'test_type': case.test_type,
            'priority': case.priority,
            'status': case.status,
            'steps': steps,
            'executions_count': len(case.test_executions),
            'created_at': case.created_at.isoformat() if case.created_at else None
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== TEST EXECUTIONS ====================

@tests_bp.route('/executions', methods=['POST'])
@jwt_required()
def create_test_execution():
    """Start a new test execution"""
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        
        case = TestCase.query.get(data.get('test_case_id'))
        if not case:
            return jsonify({'error': 'Test case not found'}), 404
        
        execution = TestExecution(
            id=str(uuid.uuid4()),
            test_case_id=case.id,
            executed_by=user_id,
            total_steps=len(case.test_steps),
            overall_status='NOT_RUN'
        )
        
        db.session.add(execution)
        db.session.commit()
        
        return jsonify({
            'message': 'Test execution started',
            'execution_id': execution.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@tests_bp.route('/executions/<execution_id>', methods=['GET'])
@jwt_required()
def get_test_execution(execution_id):
    """Get test execution details"""
    try:
        execution = TestExecution.query.get(execution_id)
        if not execution:
            return jsonify({'error': 'Test execution not found'}), 404
        
        executor = User.query.get(execution.executed_by) if execution.executed_by else None
        
        results = []
        for result in execution.test_results:
            results.append({
                'id': result.id,
                'step_id': result.step_id,
                'status': result.status,
                'actual_result': result.actual_result,
                'notes': result.notes,
                'screenshot_urls': result.screenshot_urls
            })
        
        return jsonify({
            'id': execution.id,
            'test_case_id': execution.test_case_id,
            'execution_date': execution.execution_date.isoformat() if execution.execution_date else None,
            'executed_by': {
                'id': executor.id,
                'name': f'{executor.first_name} {executor.last_name}'
            } if executor else None,
            'total_steps': execution.total_steps,
            'passed_steps': execution.passed_steps,
            'failed_steps': execution.failed_steps,
            'overall_status': execution.overall_status,
            'comments': execution.comments,
            'results': results
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tests_bp.route('/executions/<execution_id>/steps/<step_id>', methods=['POST'])
@jwt_required()
def record_step_result(execution_id, step_id):
    """Record result for a test step"""
    try:
        data = request.get_json()
        
        execution = TestExecution.query.get(execution_id)
        if not execution:
            return jsonify({'error': 'Test execution not found'}), 404
        
        result = TestStepResult(
            id=str(uuid.uuid4()),
            execution_id=execution_id,
            step_id=step_id,
            status=data.get('status'),
            actual_result=data.get('actual_result'),
            notes=data.get('notes'),
            duration_seconds=data.get('duration_seconds'),
            screenshot_urls=data.get('screenshot_urls', [])
        )
        
        db.session.add(result)
        
        # Update execution counts
        if data.get('status') == 'PASS':
            execution.passed_steps += 1
        elif data.get('status') == 'FAIL':
            execution.failed_steps += 1
        
        db.session.commit()
        
        return jsonify({
            'message': 'Step result recorded',
            'result_id': result.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@tests_bp.route('/executions/<execution_id>/complete', methods=['POST'])
@jwt_required()
def complete_test_execution(execution_id):
    """Complete a test execution"""
    try:
        data = request.get_json()
        
        execution = TestExecution.query.get(execution_id)
        if not execution:
            return jsonify({'error': 'Test execution not found'}), 404
        
        execution.overall_status = data.get('overall_status', 'PASS')
        execution.comments = data.get('comments')
        
        db.session.commit()
        
        return jsonify({'message': 'Test execution completed'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==================== STATISTICS ====================

@tests_bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_test_statistics():
    """Get overall test statistics"""
    try:
        project_id = request.args.get('project_id')
        
        query = TestPlan.query
        if project_id:
            query = query.filter(TestPlan.project_id == project_id)
        
        total_plans = query.count()
        total_cases = TestCase.query.join(TestPlan).filter(
            TestPlan.project_id == project_id if project_id else True
        ).count()
        
        total_executions = TestExecution.query.join(TestCase).join(TestPlan).filter(
            TestPlan.project_id == project_id if project_id else True
        ).count()
        
        passed_executions = TestExecution.query.join(TestCase).join(TestPlan).filter(
            TestExecution.overall_status == 'PASS',
            TestPlan.project_id == project_id if project_id else True
        ).count()
        
        failed_executions = TestExecution.query.join(TestCase).join(TestPlan).filter(
            TestExecution.overall_status == 'FAIL',
            TestPlan.project_id == project_id if project_id else True
        ).count()
        
        pass_rate = (passed_executions / total_executions * 100) if total_executions > 0 else 0
        
        return jsonify({
            'total_plans': total_plans,
            'total_cases': total_cases,
            'total_executions': total_executions,
            'passed_executions': passed_executions,
            'failed_executions': failed_executions,
            'pass_rate': round(pass_rate, 2)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
