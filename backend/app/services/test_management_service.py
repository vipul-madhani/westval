from app.models.test_management import TestPlan, TestSet, TestCase, TestStep, TestExecution, TestStepResult
from app import db
from datetime import datetime
from uuid import uuid4
import json

class TestManagementService:
    
    @staticmethod
    def create_test_plan(name, description, validation_id, project_id, created_by):
        """Create new test plan"""
        test_plan = TestPlan(
            id=str(uuid4()),
            name=name,
            description=description,
            validation_id=validation_id,
            project_id=project_id,
            created_by=created_by,
            status='DRAFT',
            created_at=datetime.utcnow()
        )
        db.session.add(test_plan)
        db.session.commit()
        return test_plan
    
    @staticmethod
    def create_test_set(test_plan_id, name, description, scope):
        """Create test set within plan"""
        test_set = TestSet(
            id=str(uuid4()),
            test_plan_id=test_plan_id,
            name=name,
            description=description,
            scope=scope,
            created_at=datetime.utcnow()
        )
        db.session.add(test_set)
        db.session.commit()
        return test_set
    
    @staticmethod
    def create_test_case(test_set_id, name, description, requirement_id=None):
        """Create test case"""
        test_case = TestCase(
            id=str(uuid4()),
            test_set_id=test_set_id,
            name=name,
            description=description,
            requirement_id=requirement_id,
            status='ACTIVE',
            created_at=datetime.utcnow()
        )
        db.session.add(test_case)
        db.session.commit()
        return test_case
    
    @staticmethod
    def add_test_step(test_case_id, step_number, action, expected_result):
        """Add step to test case"""
        test_step = TestStep(
            id=str(uuid4()),
            test_case_id=test_case_id,
            step_number=step_number,
            action=action,
            expected_result=expected_result,
            created_at=datetime.utcnow()
        )
        db.session.add(test_step)
        db.session.commit()
        return test_step
    
    @staticmethod
    def execute_test(test_case_id, executed_by):
        """Create test execution record"""
        test_execution = TestExecution(
            id=str(uuid4()),
            test_case_id=test_case_id,
            execution_date=datetime.utcnow(),
            executed_by=executed_by,
            total_steps=0,
            passed_steps=0,
            failed_steps=0,
            overall_status='IN_PROGRESS'
        )
        db.session.add(test_execution)
        db.session.commit()
        return test_execution
    
    @staticmethod
    def record_step_result(execution_id, step_id, status, actual_result, notes=None, screenshots=None):
        """Record individual step result"""
        step_result = TestStepResult(
            id=str(uuid4()),
            execution_id=execution_id,
            step_id=step_id,
            status=status,
            actual_result=actual_result,
            notes=notes,
            screenshot_urls=screenshots or [],
            duration_seconds=0
        )
        db.session.add(step_result)
        db.session.flush()
        
        # Update execution summary
        execution = TestExecution.query.get(execution_id)
        step_results = TestStepResult.query.filter_by(execution_id=execution_id).all()
        
        execution.total_steps = len(step_results)
        execution.passed_steps = len([s for s in step_results if s.status == 'PASS'])
        execution.failed_steps = len([s for s in step_results if s.status == 'FAIL'])
        
        if execution.passed_steps == execution.total_steps:
            execution.overall_status = 'PASS'
        elif execution.failed_steps > 0:
            execution.overall_status = 'FAIL'
        
        db.session.commit()
        return step_result
    
    @staticmethod
    def get_test_plan(test_plan_id):
        """Retrieve test plan with all nested data"""
        return TestPlan.query.get(test_plan_id)
    
    @staticmethod
    def get_test_coverage(validation_id):
        """Calculate test coverage metrics"""
        test_plans = TestPlan.query.filter_by(validation_id=validation_id).all()
        total_test_cases = 0
        executed_test_cases = 0
        passed_test_cases = 0
        failed_test_cases = 0
        
        for plan in test_plans:
            for test_set in plan.test_sets:
                for test_case in test_set.test_cases:
                    total_test_cases += 1
                    executions = TestExecution.query.filter_by(test_case_id=test_case.id).all()
                    if executions:
                        executed_test_cases += 1
                        latest_execution = max(executions, key=lambda x: x.execution_date)
                        if latest_execution.overall_status == 'PASS':
                            passed_test_cases += 1
                        elif latest_execution.overall_status == 'FAIL':
                            failed_test_cases += 1
        
        coverage_pct = (executed_test_cases / total_test_cases * 100) if total_test_cases > 0 else 0
        
        return {
            'total_test_cases': total_test_cases,
            'executed_test_cases': executed_test_cases,
            'passed_test_cases': passed_test_cases,
            'failed_test_cases': failed_test_cases,
            'coverage_percentage': round(coverage_pct, 2),
            'pass_rate': round(passed_test_cases / executed_test_cases * 100, 2) if executed_test_cases > 0 else 0
        }
    
    @staticmethod
    def link_requirement_to_test(test_case_id, requirement_id):
        """Link requirement to test case for traceability"""
        test_case = TestCase.query.get(test_case_id)
        test_case.requirement_id = requirement_id
        db.session.commit()
        return test_case
    
    @staticmethod
    def get_untested_requirements(validation_id):
        """Get requirements not covered by tests"""
        from app.models.requirement import Requirement
        
        requirements = Requirement.query.filter_by(validation_id=validation_id).all()
        tested_requirement_ids = set()
        
        test_plans = TestPlan.query.filter_by(validation_id=validation_id).all()
        for plan in test_plans:
            for test_set in plan.test_sets:
                for test_case in test_set.test_cases:
                    if test_case.requirement_id:
                        tested_requirement_ids.add(test_case.requirement_id)
        
        untested = [r for r in requirements if r.id not in tested_requirement_ids]
        return untested
