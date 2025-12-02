from flask import Blueprint, request, jsonify
from app.services.reporting_service import ReportingService
from app.auth import jwt_required, get_current_user
from datetime import datetime, timedelta
from app.extensions import db

reporting_bp = Blueprint('reporting', __name__, url_prefix='/api/reporting')

@reporting_bp.route('/reports', methods=['POST'])
@jwt_required()
def create_report():
    user = get_current_user()
    data = request.json
    report = ReportingService.generate_report(user.id, data['template_id'], data.get('filters', {}), db.session)
    return jsonify({'id': report.id, 'status': report.status}), 201

@reporting_bp.route('/reports/<int:report_id>', methods=['GET'])
@jwt_required()
def get_report(report_id):
    report = db.session.query(Report).filter_by(id=report_id).first()
    if not report:
        return jsonify({'error': 'Report not found'}), 404
    return jsonify({'id': report.id, 'status': report.status, 'created_at': report.created_at.isoformat()}), 200

@reporting_bp.route('/reports/<int:report_id>/schedule', methods=['POST'])
@jwt_required()
def schedule_report(report_id):
    user = get_current_user()
    data = request.json
    schedule = ReportingService.schedule_report(user.id, report_id, data['frequency'], datetime.utcnow(), db.session)
    return jsonify({'schedule_id': schedule.id, 'frequency': schedule.frequency}), 201

@reporting_bp.route('/schedules/<int:schedule_id>/execute', methods=['POST'])
@jwt_required()
def execute_schedule(schedule_id):
    user = get_current_user()
    execution = ReportingService.execute_report(user.id, schedule_id, db.session)
    return jsonify({'execution_id': execution.id, 'status': execution.status}), 200

@reporting_bp.route('/reports/<int:report_id>/export', methods=['GET'])
@jwt_required()
def export_report(report_id):
    fmt = request.args.get('format', 'csv')
    report = db.session.query(Report).filter_by(id=report_id).first()
    if not report:
        return jsonify({'error': 'Report not found'}), 404
    data = [[report.id, report.status, report.created_at]]
    csv_data = ReportingService.export_report_csv(report_id, data, db.session)
    return csv_data, 200, {'Content-Type': 'text/csv'}

@reporting_bp.route('/reports/<int:report_id>/history', methods=['GET'])
@jwt_required()
def get_execution_history(report_id):
    history = ReportingService.get_report_history(report_id, db.session)
    return jsonify([{'id': h.id, 'status': h.status, 'completed_at': h.completed_at.isoformat() if h.completed_at else None} for h in history]), 200
