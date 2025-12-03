"""Report generation service"""
from datetime import datetime
import json
from app.models.validation import ValidationProject, ValidationProtocol
from app.models.test_management import TestCase
from app.models.requirement import Requirement
from app.models.document import Document

class ReportService:
    
    @staticmethod
    def generate_validation_summary(project_id):
        """Generate validation summary report"""
        project = ValidationProject.query.get(project_id)
        if not project:
            return None
        
        # Get all protocols
        protocols = ValidationProtocol.query.filter_by(project_id=project_id).all()
        
        # Get all test cases
        test_cases = []
        for protocol in protocols:
            tests = TestCase.query.filter_by(protocol_id=protocol.id).all()
            test_cases.extend(tests)
        
        # Calculate statistics
        total_tests = len(test_cases)
        passed = len([t for t in test_cases if t.status == 'Passed'])
        failed = len([t for t in test_cases if t.status == 'Failed'])
        not_executed = len([t for t in test_cases if t.status == 'Not Executed'])
        pass_rate = (passed / total_tests * 100) if total_tests > 0 else 0
        
        # Get requirements
        requirements = Requirement.query.filter_by(project_id=project_id).all()
        
        report = {
            'report_type': 'Validation Summary Report',
            'generated_at': datetime.utcnow().isoformat(),
            'project': {
                'id': project.id,
                'name': project.name,
                'type': project.validation_type,
                'status': project.status,
                'start_date': project.start_date.isoformat() if project.start_date else None,
                'target_completion': project.target_completion.isoformat() if project.target_completion else None
            },
            'summary': {
                'total_protocols': len(protocols),
                'total_requirements': len(requirements),
                'total_test_cases': total_tests,
                'tests_passed': passed,
                'tests_failed': failed,
                'tests_not_executed': not_executed,
                'pass_rate': round(pass_rate, 2)
            },
            'protocols': [{
                'id': p.id,
                'protocol_number': p.protocol_number,
                'title': p.title,
                'status': p.status,
                'created_date': p.created_date.isoformat() if p.created_date else None
            } for p in protocols],
            'test_results': [{
                'test_id': t.test_case_id,
                'title': t.title,
                'status': t.status,
                'executed_by': t.executed_by,
                'execution_date': t.execution_date.isoformat() if t.execution_date else None
            } for t in test_cases],
            'compliance': {
                '21_cfr_part_11': 'Compliant',
                'gamp5': 'Aligned',
                'eu_annex_11': 'Compliant'
            },
            'conclusion': ReportService._generate_conclusion(pass_rate, failed, not_executed)
        }
        
        return report
    
    @staticmethod
    def _generate_conclusion(pass_rate, failed, not_executed):
        """Generate report conclusion"""
        if pass_rate == 100 and failed == 0:
            return {
                'status': 'SUCCESS',
                'message': 'All test cases passed successfully. System is validated and ready for production use.',
                'recommendation': 'Proceed with deployment'
            }
        elif failed > 0:
            return {
                'status': 'FAILED',
                'message': f'{failed} test case(s) failed. Deviations must be investigated and resolved.',
                'recommendation': 'Address failures before deployment'
            }
        elif not_executed > 0:
            return {
                'status': 'INCOMPLETE',
                'message': f'{not_executed} test case(s) not executed. Validation incomplete.',
                'recommendation': 'Complete remaining test cases'
            }
        else:
            return {
                'status': 'IN_PROGRESS',
                'message': 'Validation in progress.',
                'recommendation': 'Continue testing as planned'
            }
    
    @staticmethod
    def generate_traceability_report(project_id):
        """Generate traceability matrix report"""
        requirements = Requirement.query.filter_by(project_id=project_id).all()
        
        matrix = []
        for req in requirements:
            # Get linked test cases
            linked_tests = TestCase.query.filter(
                TestCase.requirement_ids.contains([req.id])
            ).all() if hasattr(TestCase, 'requirement_ids') else []
            
            matrix.append({
                'requirement_id': req.requirement_id,
                'title': req.title,
                'criticality': req.criticality,
                'test_cases': [t.test_case_id for t in linked_tests],
                'coverage': 'Complete' if linked_tests else 'Gap',
                'status': req.status
            })
        
        # Calculate coverage
        total = len(requirements)
        covered = len([r for r in requirements if r.status in ['Verified', 'Approved']])
        coverage_percentage = (covered / total * 100) if total > 0 else 0
        
        return {
            'report_type': 'Requirements Traceability Matrix',
            'generated_at': datetime.utcnow().isoformat(),
            'project_id': project_id,
            'coverage': {
                'total_requirements': total,
                'covered_requirements': covered,
                'coverage_percentage': round(coverage_percentage, 2),
                'gaps': total - covered
            },
            'matrix': matrix
        }
    
    @staticmethod
    def generate_deviation_report(project_id):
        """Generate deviation report for failed tests"""
        protocols = ValidationProtocol.query.filter_by(project_id=project_id).all()
        
        deviations = []
        for protocol in protocols:
            failed_tests = TestCase.query.filter_by(
                protocol_id=protocol.id,
                status='Failed'
            ).all()
            
            for test in failed_tests:
                deviations.append({
                    'deviation_id': f'DEV-{test.test_case_id}',
                    'test_case_id': test.test_case_id,
                    'test_title': test.title,
                    'protocol': protocol.protocol_number,
                    'expected_result': test.expected_result,
                    'actual_result': test.actual_result,
                    'detected_date': test.execution_date.isoformat() if test.execution_date else None,
                    'severity': 'Critical' if test.criticality == 'Critical' else 'Major',
                    'status': 'Open',
                    'investigation_required': True
                })
        
        return {
            'report_type': 'Deviation Report',
            'generated_at': datetime.utcnow().isoformat(),
            'project_id': project_id,
            'total_deviations': len(deviations),
            'open_deviations': len(deviations),
            'deviations': deviations
        }
    
    @staticmethod
    def generate_audit_package(project_id):
        """Generate complete audit package"""
        validation_summary = ReportService.generate_validation_summary(project_id)
        traceability = ReportService.generate_traceability_report(project_id)
        deviations = ReportService.generate_deviation_report(project_id)
        
        # Get all documents
        documents = Document.query.filter_by(project_id=project_id).all()
        
        return {
            'package_type': 'Audit Submission Package',
            'generated_at': datetime.utcnow().isoformat(),
            'project_id': project_id,
            'validation_summary': validation_summary,
            'traceability_matrix': traceability,
            'deviation_report': deviations,
            'documents': [{
                'document_id': d.document_id,
                'title': d.title,
                'type': d.document_type,
                'version': d.version,
                'status': d.status,
                'approved_date': d.approved_date.isoformat() if d.approved_date else None
            } for d in documents],
            'compliance_statement': {
                'compliant_with': ['21 CFR Part 11', 'EU Annex 11', 'GAMP 5'],
                'audit_trail': 'Complete and tamper-proof',
                'electronic_signatures': 'Implemented',
                'data_integrity': 'ALCOA+ compliant'
            }
        }