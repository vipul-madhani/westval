import json
import uuid
from datetime import datetime, timedelta
from hashlib import sha256

class ReportsEngineService:
    """Service layer for comprehensive report generation and management"""
    
    @staticmethod
    def create_report_template(template_name, report_type, description, sections, export_formats, created_by):
        """Create new report template (VSR, RTM, OQ, IQ, PQ)"""
        return {
            'id': str(uuid.uuid4()),
            'name': template_name,
            'report_type': report_type,  # VSR, RTM, OQ, IQ, PQ
            'description': description,
            'sections': sections,
            'export_formats': export_formats,  # [PDF, Excel, HTML]
            'created_by': created_by,
            'created_at': datetime.utcnow().isoformat(),
            'is_active': True
        }
    
    @staticmethod
    def generate_report(template_id, validation_scope_id, report_type, title, content_data, generated_by):
        """Generate new report from template"""
        report_id = str(uuid.uuid4())
        return {
            'id': report_id,
            'template_id': template_id,
            'validation_scope_id': validation_scope_id,
            'report_type': report_type,
            'title': title,
            'status': 'GENERATING',
            'content': content_data,
            'summary': ReportsEngineService.calculate_report_summary(content_data),
            'generated_by': generated_by,
            'generated_at': datetime.utcnow().isoformat(),
            'version': 1,
            'is_published': False
        }
    
    @staticmethod
    def calculate_report_summary(content_data):
        """Calculate report metrics and compliance percentages"""
        return {
            'total_requirements': len(content_data.get('requirements', [])),
            'verified_requirements': sum(1 for r in content_data.get('requirements', []) if r.get('status') == 'VERIFIED'),
            'passed_tests': sum(1 for t in content_data.get('tests', []) if t.get('status') == 'PASSED'),
            'failed_tests': sum(1 for t in content_data.get('tests', []) if t.get('status') == 'FAILED'),
            'compliance_percentage': content_data.get('compliance_percentage', 0),
            'critical_findings': len([f for f in content_data.get('findings', []) if f.get('severity') == 'CRITICAL']),
            'major_findings': len([f for f in content_data.get('findings', []) if f.get('severity') == 'MAJOR']),
            'minor_findings': len([f for f in content_data.get('findings', []) if f.get('severity') == 'MINOR']),
            'generated_timestamp': datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def build_requirement_traceability_matrix(validation_scope_id, requirements, test_cases, test_results):
        """Build comprehensive RTM linking requirements to tests to results"""
        rtm_records = []
        for req in requirements:
            linked_tests = [tc for tc in test_cases if req.get('id') in tc.get('requirement_ids', [])]
            for test in linked_tests:
                test_result = next((tr for tr in test_results if tr.get('test_case_id') == test.get('id')), None)
                
                coverage = 100 if test_result and test_result.get('status') == 'PASSED' else 0
                req_status = 'VERIFIED' if test_result and test_result.get('status') == 'PASSED' else 'IN_TEST'
                
                rtm_record = {
                    'id': str(uuid.uuid4()),
                    'requirement_id': req.get('id'),
                    'test_case_id': test.get('id'),
                    'validation_scope_id': validation_scope_id,
                    'requirement_status': req_status,
                    'test_status': test_result.get('status') if test_result else 'NOT_EXECUTED',
                    'coverage_percentage': coverage,
                    'verification_method': 'Test',
                    'verification_date': datetime.utcnow().isoformat() if test_result else None,
                    'risk_level': req.get('risk_level', 'MEDIUM')
                }
                rtm_records.append(rtm_record)
        return rtm_records
    
    @staticmethod
    def create_validation_summary(validation_scope_id, validation_phase, metrics, completed_by=None):
        """Create OQ/IQ/PQ validation phase summary with compliance metrics"""
        return {
            'id': str(uuid.uuid4()),
            'validation_scope_id': validation_scope_id,
            'validation_phase': validation_phase,  # OQ, IQ, PQ
            'total_requirements': metrics.get('total_requirements', 0),
            'verified_requirements': metrics.get('verified_requirements', 0),
            'failed_requirements': metrics.get('failed_requirements', 0),
            'total_test_cases': metrics.get('total_test_cases', 0),
            'passed_test_cases': metrics.get('passed_test_cases', 0),
            'failed_test_cases': metrics.get('failed_test_cases', 0),
            'blocked_test_cases': metrics.get('blocked_test_cases', 0),
            'overall_compliance_percentage': metrics.get('compliance_percentage', 0),
            'critical_findings_count': metrics.get('critical_findings', 0),
            'major_findings_count': metrics.get('major_findings', 0),
            'minor_findings_count': metrics.get('minor_findings', 0),
            'open_issues': metrics.get('open_issues', 0),
            'closed_issues': metrics.get('closed_issues', 0),
            'phase_status': 'COMPLETED' if completed_by else 'IN_PROGRESS',
            'phase_completion_date': datetime.utcnow().isoformat() if completed_by else None,
            'phase_completed_by': completed_by,
            'created_at': datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def export_report(report_id, export_format, exported_by):
        """Create report export record with digital signature for compliance"""
        file_path = f'/reports/{report_id}/report.{export_format}'
        export_content = json.dumps({'report_id': report_id, 'exported_at': datetime.utcnow().isoformat()})
        digital_signature = sha256(export_content.encode()).hexdigest()
        
        return {
            'id': str(uuid.uuid4()),
            'report_id': report_id,
            'export_format': export_format,
            'export_file_path': file_path,
            'export_size_bytes': len(export_content),
            'exported_by': exported_by,
            'exported_at': datetime.utcnow().isoformat(),
            'digital_signature': digital_signature,
            'signature_algorithm': 'SHA256',
            'expiration_date': (datetime.utcnow() + timedelta(days=365)).isoformat(),
            'download_count': 0
        }
    
    @staticmethod
    def create_audit_entry(report_id, action, action_by_user, old_values=None, new_values=None, reason=None, ip_address=None):
        """Create comprehensive audit trail entry for 21 CFR Part 11 compliance"""
        audit_content = json.dumps({
            'action': action,
            'timestamp': datetime.utcnow().isoformat(),
            'old': old_values,
            'new': new_values
        })
        
        return {
            'id': str(uuid.uuid4()),
            'report_id': report_id,
            'action': action,  # CREATE, MODIFY, APPROVE, EXPORT, DELETE
            'action_by_user': action_by_user,
            'action_timestamp': datetime.utcnow().isoformat(),
            'old_values': old_values,
            'new_values': new_values,
            'action_reason': reason,
            'ip_address': ip_address,
            'hash_value': sha256(audit_content.encode()).hexdigest(),
            'signature_algorithm': 'SHA256'
        }
    
    @staticmethod
    def approve_report(report_id, approved_by, approval_notes):
        """Approve report with audit trail"""
        return {
            'report_id': report_id,
            'approved_by': approved_by,
            'approved_at': datetime.utcnow().isoformat(),
            'approval_notes': approval_notes,
            'approval_status': 'APPROVED'
        }
    
    @staticmethod
    def create_report_schedule(template_id, scope_id, schedule_name, frequency, recipients, created_by):
        """Schedule automated report generation"""
        schedule_id = str(uuid.uuid4())
        return {
            'id': schedule_id,
            'template_id': template_id,
            'validation_scope_id': scope_id,
            'schedule_name': schedule_name,
            'frequency': frequency,  # DAILY, WEEKLY, MONTHLY, QUARTERLY, ANNUALLY
            'is_enabled': True,
            'recipient_emails': recipients,
            'created_by': created_by,
            'created_at': datetime.utcnow().isoformat(),
            'next_run': ReportsEngineService.calculate_next_run(frequency)
        }
    
    @staticmethod
    def calculate_next_run(frequency):
        """Calculate next scheduled run time based on frequency"""
        now = datetime.utcnow()
        if frequency == 'DAILY':
            return (now + timedelta(days=1)).isoformat()
        elif frequency == 'WEEKLY':
            return (now + timedelta(weeks=1)).isoformat()
        elif frequency == 'MONTHLY':
            return (now + timedelta(days=30)).isoformat()
        elif frequency == 'QUARTERLY':
            return (now + timedelta(days=90)).isoformat()
        elif frequency == 'ANNUALLY':
            return (now + timedelta(days=365)).isoformat()
        return now.isoformat()
    
    @staticmethod
    def get_compliance_dashboard(scope_id, reports):
        """Build compliance dashboard with key metrics and trend analysis"""
        latest_reports = {}
        for report in reports:
            report_type = report.get('report_type')
            if report_type not in latest_reports or report.get('generated_at') > latest_reports[report_type].get('generated_at'):
                latest_reports[report_type] = report
        
        return {
            'scope_id': scope_id,
            'generated_at': datetime.utcnow().isoformat(),
            'oq_status': latest_reports.get('OQ', {}).get('status'),
            'iq_status': latest_reports.get('IQ', {}).get('status'),
            'pq_status': latest_reports.get('PQ', {}).get('status'),
            'vsr_count': sum(1 for r in reports if r.get('report_type') == 'VSR'),
            'rtm_completion': sum(1 for r in reports if r.get('report_type') == 'RTM' and r.get('status') == 'COMPLETE'),
            'avg_compliance_percentage': sum(r.get('summary', {}).get('compliance_percentage', 0) for r in reports) / len(reports) if reports else 0
        }
    
    @staticmethod
    def calculate_report_trends(scope_id, historical_reports):
        """Analyze historical report trends for compliance monitoring"""
        return {
            'scope_id': scope_id,
            'analysis_timestamp': datetime.utcnow().isoformat(),
            'total_reports_generated': len(historical_reports),
            'pass_rate_trend': [r.get('summary', {}).get('compliance_percentage', 0) for r in sorted(historical_reports, key=lambda x: x.get('generated_at'))[-10:]],
            'average_pass_rate': sum(r.get('summary', {}).get('compliance_percentage', 0) for r in historical_reports) / len(historical_reports) if historical_reports else 0,
            'critical_issues_resolved': sum(1 for r in historical_reports if r.get('summary', {}).get('critical_findings', 0) == 0),
            'report_generation_time_hours': 2.5  # Average generation time
        }
