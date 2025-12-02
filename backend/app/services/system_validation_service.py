import hashlib
import json
from datetime import datetime
from ..models.system_validation import ValidationProtocol, ValidationResult, ComprehensiveAuditLog, SystemHealthMetric, ValidationStatus, ValidationPhase
from sqlalchemy import db

class SystemValidationService:
    
    @staticmethod
    def create_validation_protocol(protocol_name, phase, scope, acceptance_criteria, created_by_id):
        protocol = ValidationProtocol(
            protocol_name=protocol_name,
            phase=phase,
            scope=scope,
            acceptance_criteria=acceptance_criteria,
            created_by_id=created_by_id,
            status=ValidationStatus.PLANNED
        )
        db.session.add(protocol)
        db.session.commit()
        return protocol
    
    @staticmethod
    def execute_validation_test(protocol_id, test_case, expected_outcome, actual_outcome, executed_by_id):
        result = ValidationResult(
            protocol_id=protocol_id,
            test_case=test_case,
            expected_outcome=expected_outcome,
            actual_outcome=actual_outcome,
            passed=(expected_outcome == actual_outcome),
            executed_by_id=executed_by_id
        )
        db.session.add(result)
        db.session.commit()
        return result
    
    @staticmethod
    def approve_protocol(protocol_id, approved_by_id):
        protocol = ValidationProtocol.query.get(protocol_id)
        if protocol:
            protocol.status = ValidationStatus.APPROVED
            protocol.approved_by_id = approved_by_id
            protocol.approved_at = datetime.utcnow()
            db.session.commit()
        return protocol
    
    @staticmethod
    def log_comprehensive_audit(audit_type, entity_type, entity_id, action, user_id, old_values=None, new_values=None, ip_address=None, user_agent=None):
        audit_data = {
            'old': old_values,
            'new': new_values
        }
        checksum = hashlib.sha256(json.dumps(audit_data, sort_keys=True).encode()).hexdigest()
        
        audit_log = ComprehensiveAuditLog(
            audit_type=audit_type,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            old_values=json.dumps(old_values) if old_values else None,
            new_values=json.dumps(new_values) if new_values else None,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            checksum=checksum
        )
        db.session.add(audit_log)
        db.session.commit()
        return audit_log
    
    @staticmethod
    def record_system_health_metric(metric_name, metric_value, threshold_min=None, threshold_max=None):
        status = 'OK'
        if threshold_min and metric_value < threshold_min:
            status = 'LOW'
        elif threshold_max and metric_value > threshold_max:
            status = 'HIGH'
        
        metric = SystemHealthMetric(
            metric_name=metric_name,
            metric_value=metric_value,
            threshold_min=threshold_min,
            threshold_max=threshold_max,
            status=status
        )
        db.session.add(metric)
        db.session.commit()
        return metric
    
    @staticmethod
    def get_validation_summary(protocol_id):
        protocol = ValidationProtocol.query.get(protocol_id)
        if not protocol:
            return None
        
        results = ValidationResult.query.filter_by(protocol_id=protocol_id).all()
        total_tests = len(results)
        passed_tests = len([r for r in results if r.passed])
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        return {
            'protocol_id': protocol_id,
            'protocol_name': protocol.protocol_name,
            'phase': protocol.phase.value,
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'pass_rate': pass_rate,
            'status': protocol.status.value
        }
    
    @staticmethod
    def generate_audit_report(start_date, end_date):
        logs = ComprehensiveAuditLog.query.filter(
            ComprehensiveAuditLog.timestamp >= start_date,
            ComprehensiveAuditLog.timestamp <= end_date
        ).all()
        
        report = {
            'total_audit_records': len(logs),
            'audit_types': {},
            'by_user': {},
            'by_entity': {}
        }
        
        for log in logs:
            report['audit_types'][log.audit_type] = report['audit_types'].get(log.audit_type, 0) + 1
            report['by_user'][log.user_id] = report['by_user'].get(log.user_id, 0) + 1
            report['by_entity'][log.entity_type] = report['by_entity'].get(log.entity_type, 0) + 1
        
        return report
