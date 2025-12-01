from flask import Blueprint, request, jsonify
from app.services.risk_management_service import RiskManagementService
from functools import wraps

risk_bp = Blueprint('risk', __name__, url_prefix='/api/risk')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not request.headers.get('Authorization'):
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated

@risk_bp.route('/create', methods=['POST'])
@token_required
def create_risk():
    data = request.json
    risk = RiskManagementService.create_risk(
        data['project_id'], data['description'],
        data['category'], data['severity'],
        data['probability'], data['owner_id']
    )
    return jsonify({'risk_id': risk.id, 'rpn': risk.rpn}), 201

@risk_bp.route('/<int:risk_id>/mitigation', methods=['PUT'])
@token_required
def update_mitigation(risk_id):
    data = request.json
    risk = RiskManagementService.update_risk_mitigation(
        risk_id, data.get('strategy'), data.get('status')
    )
    return jsonify({'status': 'updated'}), 200

@risk_bp.route('/project/<int:project_id>/high', methods=['GET'])
@token_required
def get_high_risks(project_id):
    threshold = request.args.get('threshold', 50, type=int)
    risks = RiskManagementService.get_high_risk_items(project_id, threshold)
    return jsonify([{'id': r.id, 'rpn': r.rpn, 'category': r.risk_category} for r in risks]), 200

@risk_bp.route('/fmea/<int:fmea_id>', methods=['POST'])
@token_required
def add_failure_mode(fmea_id):
    data = request.json
    mode = RiskManagementService.add_failure_mode(
        fmea_id, data['description'],
        data['severity'], data['occurrence'], data['detection']
    )
    return jsonify({'mode_id': mode.id, 'rpn': mode.rpn}), 201

@risk_bp.route('/fmea/<int:fmea_id>/summary', methods=['GET'])
@token_required
def get_fmea_summary(fmea_id):
    summary = RiskManagementService.get_fmea_summary(fmea_id)
    return jsonify({'total_modes': len(summary['modes']), 'high_risk_count': len(summary['high_risk'])}), 200
