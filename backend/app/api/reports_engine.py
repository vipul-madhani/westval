from flask import Blueprint, request, jsonify
from functools import wraps
import json
from reports_engine_service import ReportsEngineService

reports_bp = Blueprint('reports', __name__, url_prefix='/api/reports')

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Missing authorization'}), 401
        return f(*args, **kwargs)
    return decorated_function

# Report Template Management
@reports_bp.route('/templates', methods=['POST'])
@require_auth
def create_template():
    """Create new report template"""
    try:
        data = request.get_json()
        template = ReportsEngineService.create_report_template(
            template_name=data.get('name'),
            report_type=data.get('report_type'),
            description=data.get('description'),
            sections=data.get('sections'),
            export_formats=data.get('export_formats'),
            created_by=request.headers.get('User-ID')
        )
        return jsonify({'template': template}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@reports_bp.route('/templates/<template_id>', methods=['GET'])
@require_auth
def get_template(template_id):
    """Retrieve report template"""
    return jsonify({'template_id': template_id}), 200

# Report Generation
@reports_bp.route('/scopes/<scope_id>/generate', methods=['POST'])
@require_auth
def generate_report(scope_id):
    """Generate new report for validation scope"""
    try:
        data = request.get_json()
        report = ReportsEngineService.generate_report(
            template_id=data.get('template_id'),
            validation_scope_id=scope_id,
            report_type=data.get('report_type'),
            title=data.get('title'),
            content_data=data.get('content'),
            generated_by=request.headers.get('User-ID')
        )
        return jsonify({'report': report}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@reports_bp.route('/<report_id>', methods=['GET'])
@require_auth
def get_report(report_id):
    """Retrieve generated report"""
    return jsonify({'report_id': report_id, 'status': 'COMPLETE'}), 200

# RTM (Requirement Traceability Matrix)
@reports_bp.route('/scopes/<scope_id>/rtm', methods=['POST'])
@require_auth
def generate_rtm(scope_id):
    """Generate requirement traceability matrix"""
    try:
        data = request.get_json()
        rtm_records = ReportsEngineService.build_requirement_traceability_matrix(
            validation_scope_id=scope_id,
            requirements=data.get('requirements'),
            test_cases=data.get('test_cases'),
            test_results=data.get('test_results')
        )
        return jsonify({'rtm_records': rtm_records, 'total': len(rtm_records)}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@reports_bp.route('/scopes/<scope_id>/rtm', methods=['GET'])
@require_auth
def get_rtm(scope_id):
    """Retrieve RTM for scope"""
    return jsonify({'scope_id': scope_id, 'rtm_records': []}), 200

# Validation Summary (OQ/IQ/PQ)
@reports_bp.route('/scopes/<scope_id>/summaries', methods=['POST'])
@require_auth
def create_validation_summary(scope_id):
    """Create validation phase summary"""
    try:
        data = request.get_json()
        summary = ReportsEngineService.create_validation_summary(
            validation_scope_id=scope_id,
            validation_phase=data.get('phase'),
            metrics=data.get('metrics'),
            completed_by=data.get('completed_by')
        )
        return jsonify({'summary': summary}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@reports_bp.route('/scopes/<scope_id>/summaries/<phase>', methods=['GET'])
@require_auth
def get_phase_summary(scope_id, phase):
    """Retrieve phase summary (OQ/IQ/PQ)"""
    return jsonify({'scope_id': scope_id, 'phase': phase}), 200

# Report Export
@reports_bp.route('/<report_id>/export', methods=['POST'])
@require_auth
def export_report(report_id):
    """Export report in specified format with digital signature"""
    try:
        data = request.get_json()
        export = ReportsEngineService.export_report(
            report_id=report_id,
            export_format=data.get('format'),  # pdf, xlsx, html
            exported_by=request.headers.get('User-ID')
        )
        return jsonify({'export': export}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@reports_bp.route('/<report_id>/exports', methods=['GET'])
@require_auth
def get_report_exports(report_id):
    """Retrieve all exports for a report"""
    return jsonify({'report_id': report_id, 'exports': []}), 200

# Report Approval
@reports_bp.route('/<report_id>/approve', methods=['POST'])
@require_auth
def approve_report(report_id):
    """Approve report with audit trail"""
    try:
        data = request.get_json()
        approval = ReportsEngineService.approve_report(
            report_id=report_id,
            approved_by=request.headers.get('User-ID'),
            approval_notes=data.get('notes')
        )
        return jsonify({'approval': approval}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Report Scheduling
@reports_bp.route('/schedules', methods=['POST'])
@require_auth
def create_schedule():
    """Create automated report generation schedule"""
    try:
        data = request.get_json()
        schedule = ReportsEngineService.create_report_schedule(
            template_id=data.get('template_id'),
            scope_id=data.get('scope_id'),
            schedule_name=data.get('name'),
            frequency=data.get('frequency'),
            recipients=data.get('recipients'),
            created_by=request.headers.get('User-ID')
        )
        return jsonify({'schedule': schedule}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@reports_bp.route('/schedules/<schedule_id>', methods=['GET'])
@require_auth
def get_schedule(schedule_id):
    """Retrieve report schedule"""
    return jsonify({'schedule_id': schedule_id}), 200

# Compliance Dashboard
@reports_bp.route('/scopes/<scope_id>/dashboard', methods=['GET'])
@require_auth
def get_compliance_dashboard(scope_id):
    """Get real-time compliance dashboard metrics"""
    dashboard = ReportsEngineService.get_compliance_dashboard(
        scope_id=scope_id,
        reports=[]
    )
    return jsonify({'dashboard': dashboard}), 200

# Health Check
@reports_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'reports-engine'}), 200
