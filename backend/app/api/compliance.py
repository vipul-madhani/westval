"""Compliance and audit trail API"""
from flask import Blueprint

compliance_bp = Blueprint('compliance', __name__)

@compliance_bp.route('/audit-trail', methods=['GET'])
def audit_trail():
    return {'message': 'Audit trail endpoint'}, 200

@compliance_bp.route('/dashboard', methods=['GET'])
def compliance_dashboard():
    return {'message': 'Compliance dashboard endpoint'}, 200