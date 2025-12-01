"""Risk assessment API"""
from flask import Blueprint

risk_bp = Blueprint('risk', __name__)

@risk_bp.route('/assessments', methods=['GET', 'POST'])
def risk_assessments():
    return {'message': 'Risk assessments endpoint'}, 200