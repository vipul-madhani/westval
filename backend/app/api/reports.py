"""Reports API endpoints"""
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.report_service import ReportService
import json
import io

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/projects/<project_id>/reports/validation-summary', methods=['GET'])
@jwt_required()
def get_validation_summary(project_id):
    """Get validation summary report"""
    report = ReportService.generate_validation_summary(project_id)
    
    if not report:
        return jsonify({'error': 'Project not found'}), 404
    
    return jsonify(report), 200

@reports_bp.route('/projects/<project_id>/reports/traceability', methods=['GET'])
@jwt_required()
def get_traceability_report(project_id):
    """Get traceability matrix report"""
    report = ReportService.generate_traceability_report(project_id)
    return jsonify(report), 200

@reports_bp.route('/projects/<project_id>/reports/deviations', methods=['GET'])
@jwt_required()
def get_deviation_report(project_id):
    """Get deviation report"""
    report = ReportService.generate_deviation_report(project_id)
    return jsonify(report), 200

@reports_bp.route('/projects/<project_id>/reports/audit-package', methods=['GET'])
@jwt_required()
def get_audit_package(project_id):
    """Get complete audit package"""
    package = ReportService.generate_audit_package(project_id)
    return jsonify(package), 200

@reports_bp.route('/projects/<project_id>/reports/export', methods=['POST'])
@jwt_required()
def export_report(project_id):
    """Export report to PDF/Excel"""
    data = request.get_json()
    report_type = data.get('report_type', 'validation_summary')
    export_format = data.get('format', 'json')  # json, pdf, excel
    
    # Generate report
    if report_type == 'validation_summary':
        report = ReportService.generate_validation_summary(project_id)
    elif report_type == 'traceability':
        report = ReportService.generate_traceability_report(project_id)
    elif report_type == 'deviations':
        report = ReportService.generate_deviation_report(project_id)
    elif report_type == 'audit_package':
        report = ReportService.generate_audit_package(project_id)
    else:
        return jsonify({'error': 'Invalid report type'}), 400
    
    if export_format == 'json':
        # Return JSON
        output = io.BytesIO()
        output.write(json.dumps(report, indent=2).encode())
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/json',
            as_attachment=True,
            download_name=f'{report_type}_{project_id}.json'
        )
    
    # For PDF/Excel, return placeholder
    return jsonify({
        'message': f'{export_format.upper()} export initiated',
        'download_url': f'/downloads/{project_id}_{report_type}.{export_format}'
    }), 200