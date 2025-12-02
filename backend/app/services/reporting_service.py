from app.models.reporting_engine import Report, ReportSchedule, ReportExecution
from app.models.auth_models import User
from app.utils.audit import log_audit_event
from datetime import datetime, timedelta
import hashlib, json
from io import BytesIO
import csv

class ReportingService:
    @staticmethod
    def generate_report(user_id, report_template_id, filters, db_session):
        user = db_session.query(User).filter_by(id=user_id).first()
        if not user:
            raise ValueError("User not found")
        report = Report(
            template_id=report_template_id,
            created_by_id=user_id,
            filters=json.dumps(filters),
            status='GENERATED'
        )
        db_session.add(report)
        db_session.commit()
        log_audit_event(user_id, f'REPORT_GENERATED', f'Report {report.id} generated', db_session)
        return report
    
    @staticmethod
    def schedule_report(user_id, report_id, frequency, next_run_time, db_session):
        report = db_session.query(Report).filter_by(id=report_id).first()
        if not report:
            raise ValueError("Report not found")
        schedule = ReportSchedule(
            report_id=report_id,
            created_by_id=user_id,
            frequency=frequency,
            next_run_time=next_run_time,
            is_active=True
        )
        db_session.add(schedule)
        db_session.commit()
        log_audit_event(user_id, f'REPORT_SCHEDULED', f'Report {report_id} scheduled', db_session)
        return schedule
    
    @staticmethod
    def execute_report(user_id, schedule_id, db_session):
        schedule = db_session.query(ReportSchedule).filter_by(id=schedule_id).first()
        if not schedule:
            raise ValueError("Schedule not found")
        execution = ReportExecution(
            schedule_id=schedule_id,
            executed_by_id=user_id,
            status='COMPLETED',
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )
        db_session.add(execution)
        schedule.last_executed_at = datetime.utcnow()
        if schedule.frequency == 'DAILY':
            schedule.next_run_time = datetime.utcnow() + timedelta(days=1)
        elif schedule.frequency == 'WEEKLY':
            schedule.next_run_time = datetime.utcnow() + timedelta(weeks=1)
        db_session.commit()
        log_audit_event(user_id, f'REPORT_EXECUTED', f'Execution {execution.id} completed', db_session)
        return execution
    
    @staticmethod
    def export_report_csv(report_id, data, db_session):
        output = BytesIO()
        writer = csv.writer(output)
        for row in data:
            writer.writerow(row)
        output.seek(0)
        return output.getvalue()
    
    @staticmethod
    def get_report_history(report_id, db_session):
        return db_session.query(ReportExecution).filter_by(report_id=report_id).all()
