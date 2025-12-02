from flask import Blueprint, request, jsonify
from app.services.compliance_service import ComplianceService
from app.auth import jwt_required, get_current_user
from app.extensions import db

comp_bp = Blueprint('compliance', __name__, url_prefix='/api/compliance')

@comp_bp.route('/docs', methods=['POST'])
@jwt_required()
def create_doc():
    user = get_current_user()
    data = request.json
    doc = ComplianceService.create_doc(user.id, data['type'], data['title'], data['content'], data.get('req_id'), db)
    return jsonify({'id': doc.id, 'status': doc.status}), 201

@comp_bp.route('/docs/<int:doc_id>', methods=['GET'])
@jwt_required()
def get_doc(doc_id):
    doc = db.query(ComplianceDocument).filter_by(id=doc_id).first()
    return jsonify({'id': doc.id, 'title': doc.title, 'status': doc.status}), 200

@comp_bp.route('/trace', methods=['POST'])
@jwt_required()
def create_trace():
    user = get_current_user()
    data = request.json
    trace = ComplianceService.trace_requirement(user.id, data['req_id'], data['doc_id'], db)
    return jsonify({'id': trace.id, 'status': trace.status}), 201

@comp_bp.route('/docs/<int:doc_id>/traceability', methods=['GET'])
@jwt_required()
def get_traceability(doc_id):
    traces = ComplianceService.get_doc_traceability(doc_id, db)
    return jsonify(traces), 200
